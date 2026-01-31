#!/usr/bin/env python3
"""
FIDE Chess Titles Data Fetcher and Processor - FINAL VERSION with Dates
Tracks GM/WGM additions with dates for future AI article generation
"""

import xml.etree.ElementTree as ET
import json
import hashlib
import logging
import urllib.request
import zipfile
from datetime import datetime
from collections import defaultdict
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fide_update.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# FIDE download URL
FIDE_URL = "https://ratings.fide.com/download/standard_rating_list_xml.zip"

# Valid titles (excluding WH as per your requirements)
VALID_TITLES = ['GM', 'IM', 'FM', 'CM', 'WGM', 'WIM', 'WFM', 'WCM']

class FIDEDataProcessor:
    def __init__(self):
        self.filtered_data = []
        self.country_data = defaultdict(lambda: {
            'Active': {title: 0 for title in VALID_TITLES},
            'Inactive': {title: 0 for title in VALID_TITLES},
            'Total': {title: 0 for title in VALID_TITLES}
        })

    def download_fide_data(self):
        """Download FIDE XML data"""
        try:
            logger.info(f"Downloading FIDE data from {FIDE_URL}")

            os.makedirs('temp', exist_ok=True)

            req = urllib.request.Request(FIDE_URL)
            req.add_header('User-Agent', 'Mozilla/5.0 (ChessTitlesMap Bot)')

            with urllib.request.urlopen(req, timeout=300) as response:
                zip_data = response.read()

            zip_path = 'temp/fide_data.zip'
            with open(zip_path, 'wb') as f:
                f.write(zip_data)

            logger.info(f"Downloaded {len(zip_data)} bytes")

            # Extract XML from zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
                if not files:
                    raise Exception("No XML file found in zip")

                xml_file = files[0]
                zip_ref.extract(xml_file, 'temp')

            xml_path = f'temp/{xml_file}'
            logger.info(f"Extracted XML file: {xml_path}")

            return xml_path

        except Exception as e:
            logger.error(f"Failed to download FIDE data: {e}")
            raise

    def calculate_file_hash(self, filepath):
        """Calculate MD5 hash to detect changes"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash: {e}")
            return None

    def check_if_data_changed(self, xml_path):
        """Check if data changed from last update"""
        try:
            current_hash = self.calculate_file_hash(xml_path)

            if os.path.exists('data/metadata.json'):
                with open('data/metadata.json', 'r') as f:
                    metadata = json.load(f)
                    last_hash = metadata.get('file_hash')

                    if current_hash == last_hash:
                        logger.info("No changes detected in FIDE data (same file hash)")
                        return False, current_hash

            logger.info("New data detected or first run")
            return True, current_hash

        except Exception as e:
            logger.warning(f"Could not check previous hash: {e}. Proceeding with update.")
            return True, current_hash

    def parse_xml_data(self, xml_path):
        """Parse FIDE XML and filter data according to your specifications"""
        try:
            logger.info("Parsing XML data...")

            tree = ET.parse(xml_path)
            root = tree.getroot()

            total_players = 0
            filtered_players = 0

            for player in root.findall('player'):
                total_players += 1

                # Extract only the fields we need (as per your filters)
                fideid = self.get_text(player, 'fideid')
                name = self.get_text(player, 'name')
                country = self.get_text(player, 'country')
                title = self.get_text(player, 'title')  # ONLY use title tag
                flag = self.get_text(player, 'flag')

                # Note: We ignore these fields as per your requirements:
                # - w_title (redundant)
                # - o_title (not needed)
                # - foa_title (not needed)
                # - games (not needed)
                # - k (not needed)

                # Filter 1: Remove records where country equals "Non" or empty
                if country == "Non" or not country:
                    continue

                # Filter 2: Remove WH title
                if title == 'WH':
                    continue

                # Filter 3: Only keep titled players (non-empty title)
                if not title or title not in VALID_TITLES:
                    continue

                # Filter 4: Clean flag - erase 'w', replace 'wi' with 'i'
                if flag:
                    flag = flag.replace('wi', 'i').replace('w', '')

                # Determine if player is active or inactive
                # 'i' flag means inactive
                is_active = 'i' not in flag

                # Store filtered player data
                self.filtered_data.append({
                    'fideid': fideid,
                    'name': name,
                    'country': country,
                    'title': title,
                    'is_active': is_active
                })

                filtered_players += 1

            logger.info(f"Parsed {total_players} total players, kept {filtered_players} titled players")
            return True

        except Exception as e:
            logger.error(f"Failed to parse XML: {e}")
            import traceback
            traceback.print_exc()
            raise

    def get_text(self, element, tag_name):
        """Safely get text content from XML element"""
        child = element.find(tag_name)
        if child is not None and child.text:
            return child.text.strip()
        return ''

    def aggregate_by_country(self):
        """Aggregate player counts by country"""
        try:
            logger.info("Aggregating data by country...")

            for player in self.filtered_data:
                country = player['country']
                title = player['title']
                is_active = player['is_active']

                # Increment Total
                self.country_data[country]['Total'][title] += 1

                # Increment Active or Inactive
                if is_active:
                    self.country_data[country]['Active'][title] += 1
                else:
                    self.country_data[country]['Inactive'][title] += 1

            logger.info(f"Aggregated data for {len(self.country_data)} countries")
            return True

        except Exception as e:
            logger.error(f"Failed to aggregate data: {e}")
            raise

    def remove_countries_with_no_titles(self):
        """Remove countries that have ZERO titled players"""
        try:
            countries_to_remove = []

            for country, data in self.country_data.items():
                # Check if country has ANY titled players
                total_count = sum(data['Total'].values())

                if total_count == 0:
                    countries_to_remove.append(country)

            for country in countries_to_remove:
                del self.country_data[country]
                logger.info(f"Removed country with no titles: {country}")

            if countries_to_remove:
                logger.info(f"Removed {len(countries_to_remove)} countries with no titled players")

            return True

        except Exception as e:
            logger.error(f"Failed to remove empty countries: {e}")
            return False

    def generate_json_output(self):
        """Generate JSON matching your exact format"""
        try:
            logger.info("Generating JSON output...")

            output = {
                "titled_players_by_country": []
            }

            # Sort countries alphabetically
            for country in sorted(self.country_data.keys()):
                data = self.country_data[country]

                country_entry = {
                    "Country": country,
                    "Active": {k: v for k, v in data['Active'].items()},
                    "Inactive": {k: v for k, v in data['Inactive'].items()},
                    "Total": {k: v for k, v in data['Total'].items()}
                }

                output["titled_players_by_country"].append(country_entry)

            return output

        except Exception as e:
            logger.error(f"Failed to generate JSON: {e}")
            raise

    def track_monthly_changes(self, new_data):
        """Track title additions/removals and new/removed countries"""
        try:
            logger.info("Tracking monthly changes...")

            os.makedirs('data', exist_ok=True)

            current_month = datetime.now().strftime('%Y-%m')
            current_date = datetime.now().strftime('%Y-%m-%d')

            # Load existing monthly changes
            monthly_changes_path = 'data/monthly_changes.json'
            if os.path.exists(monthly_changes_path):
                with open(monthly_changes_path, 'r') as f:
                    monthly_changes = json.load(f)
            else:
                monthly_changes = {}

            # Load previous data for comparison
            if os.path.exists('titled_players_by_country.json'):
                with open('titled_players_by_country.json', 'r') as f:
                    old_data_raw = json.load(f)

                # Convert old data to dict
                old_data = {}
                for entry in old_data_raw.get('titled_players_by_country', []):
                    old_data[entry['Country']] = entry

                # Calculate changes
                changes = {
                    'date': current_date,
                    'added': 0,
                    'removed': 0,
                    'by_title': {title: {'added': 0, 'removed': 0} for title in VALID_TITLES},
                    'new_countries': [],
                    'removed_countries': []
                }

                # Check for new countries
                new_countries = set(self.country_data.keys()) - set(old_data.keys())
                for country in sorted(new_countries):
                    changes['new_countries'].append(country)
                    logger.info(f"NEW COUNTRY with titled players: {country}")

                # Check for removed countries
                removed_countries = set(old_data.keys()) - set(self.country_data.keys())
                for country in sorted(removed_countries):
                    changes['removed_countries'].append(country)
                    logger.info(f"REMOVED COUNTRY (no more titled players): {country}")

                # Compare Total counts
                all_countries = set(old_data.keys()) | set(self.country_data.keys())

                for country in all_countries:
                    for title in VALID_TITLES:
                        old_count = old_data.get(country, {}).get('Total', {}).get(title, 0)
                        new_count = self.country_data.get(country, {}).get('Total', {}).get(title, 0)

                        diff = new_count - old_count

                        if diff > 0:
                            changes['added'] += diff
                            changes['by_title'][title]['added'] += diff
                        elif diff < 0:
                            changes['removed'] += abs(diff)
                            changes['by_title'][title]['removed'] += abs(diff)

                changes['total_changes'] = changes['added'] + changes['removed']
                changes['net_change'] = changes['added'] - changes['removed']

                monthly_changes[current_month] = changes

                # Save monthly changes
                with open(monthly_changes_path, 'w') as f:
                    json.dump(monthly_changes, f, indent=2)

                logger.info(f"Monthly changes: +{changes['added']}, -{changes['removed']}, net: {changes['net_change']}")

                # Log title-specific changes
                for title in VALID_TITLES:
                    added = changes['by_title'][title]['added']
                    removed = changes['by_title'][title]['removed']
                    if added > 0 or removed > 0:
                        logger.info(f"  {title}: +{added}, -{removed}")

            else:
                logger.info("No previous data found for comparison (first run)")

            return True

        except Exception as e:
            logger.error(f"Failed to track monthly changes: {e}")
            return False

    def track_new_gm_wgm(self):
        """Track new GMs and WGMs with names and dates for AI article generation"""
        try:
            logger.info("Tracking new GMs and WGMs...")

            current_month = datetime.now().strftime('%Y-%m')
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_date_full = datetime.now().strftime('%B %d, %Y')

            # Load existing GM/WGM history
            gm_history_path = 'data/new_gm_wgm_history.json'
            if os.path.exists(gm_history_path):
                with open(gm_history_path, 'r') as f:
                    gm_history = json.load(f)
            else:
                gm_history = {}

            # Build current GM/WGM set with full player info
            current_gms = {}  # fideid -> player info
            current_wgms = {}

            for player in self.filtered_data:
                if player['title'] == 'GM':
                    current_gms[player['fideid']] = {
                        'name': player['name'],
                        'country': player['country'],
                        'fideid': player['fideid']
                    }
                elif player['title'] == 'WGM':
                    current_wgms[player['fideid']] = {
                        'name': player['name'],
                        'country': player['country'],
                        'fideid': player['fideid']
                    }

            # Load previous GM/WGM list
            if os.path.exists('data/gm_wgm_list.json'):
                with open('data/gm_wgm_list.json', 'r') as f:
                    previous_list = json.load(f)
                    previous_gms = set(previous_list.get('GM', []))
                    previous_wgms = set(previous_list.get('WGM', []))

                # Find NEW GMs and WGMs
                new_gm_ids = set(current_gms.keys()) - previous_gms
                new_wgm_ids = set(current_wgms.keys()) - previous_wgms

                # Find REMOVED GMs and WGMs (those who lost their title)
                removed_gm_ids = previous_gms - set(current_gms.keys())
                removed_wgm_ids = previous_wgms - set(current_wgms.keys())

                new_gms = []
                new_wgms = []

                for fideid in new_gm_ids:
                    player_info = current_gms[fideid]
                    player_info['date_added'] = current_date
                    player_info['date_added_full'] = current_date_full
                    new_gms.append(player_info)

                for fideid in new_wgm_ids:
                    player_info = current_wgms[fideid]
                    player_info['date_added'] = current_date
                    player_info['date_added_full'] = current_date_full
                    new_wgms.append(player_info)

                if new_gms or new_wgms or removed_gm_ids or removed_wgm_ids:
                    gm_history[current_month] = {
                        'date': current_date,
                        'date_full': current_date_full,
                        'GM': {
                            'added': new_gms,
                            'removed': list(removed_gm_ids) if removed_gm_ids else []
                        },
                        'WGM': {
                            'added': new_wgms,
                            'removed': list(removed_wgm_ids) if removed_wgm_ids else []
                        }
                    }

                    logger.info(f"Found {len(new_gms)} new GMs and {len(new_wgms)} new WGMs")

                    if removed_gm_ids:
                        logger.info(f"Removed {len(removed_gm_ids)} GMs (title lost)")
                    if removed_wgm_ids:
                        logger.info(f"Removed {len(removed_wgm_ids)} WGMs (title lost)")

                    # Log names of new GMs/WGMs
                    for gm in new_gms:
                        logger.info(f"  NEW GM: {gm['name']} ({gm['country']}) - Added: {current_date_full}")
                    for wgm in new_wgms:
                        logger.info(f"  NEW WGM: {wgm['name']} ({wgm['country']}) - Added: {current_date_full}")

            # Save current GM/WGM list for next comparison
            with open('data/gm_wgm_list.json', 'w') as f:
                json.dump({
                    'GM': list(current_gms.keys()), 
                    'WGM': list(current_wgms.keys())
                }, f)

            # Save GM/WGM history
            with open(gm_history_path, 'w') as f:
                json.dump(gm_history, f, indent=2)

            logger.info(f"Total worldwide: {len(current_gms)} GMs, {len(current_wgms)} WGMs")

            return True

        except Exception as e:
            logger.error(f"Failed to track GM/WGM: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_metadata(self, file_hash):
        """Save metadata with update date and file hash"""
        try:
            metadata = {
                'last_updated': datetime.now().strftime('%B %d, %Y'),
                'last_updated_iso': datetime.now().isoformat(),
                'file_hash': file_hash
            }

            os.makedirs('data', exist_ok=True)

            with open('data/metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Metadata saved: {metadata['last_updated']}")
            return True

        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return False

    def save_json_file(self, output):
        """Save the main JSON file"""
        try:
            with open('titled_players_by_country.json', 'w') as f:
                json.dump(output, f, indent=2)

            logger.info("JSON file saved successfully: titled_players_by_country.json")
            return True

        except Exception as e:
            logger.error(f"Failed to save JSON file: {e}")
            raise


def main():
    """Main execution function"""
    try:
        logger.info("=" * 60)
        logger.info("FIDE Data Update Process Started")
        logger.info("=" * 60)

        # Create necessary directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('temp', exist_ok=True)

        processor = FIDEDataProcessor()

        # Step 1: Download FIDE XML
        xml_path = processor.download_fide_data()

        # Step 2: Check if data changed
        data_changed, file_hash = processor.check_if_data_changed(xml_path)

        if not data_changed:
            logger.info("No update needed. Exiting.")
            return 0

        # Step 3: Parse XML and filter
        processor.parse_xml_data(xml_path)

        # Step 4: Aggregate by country
        processor.aggregate_by_country()

        # Step 5: Remove countries with no titles
        processor.remove_countries_with_no_titles()

        # Step 6: Generate JSON output
        output = processor.generate_json_output()

        # Step 7: Track monthly changes (including new/removed countries)
        processor.track_monthly_changes(output)

        # Step 8: Track new GMs/WGMs with dates
        processor.track_new_gm_wgm()

        # Step 9: Save JSON file
        processor.save_json_file(output)

        # Step 10: Save metadata
        processor.save_metadata(file_hash)

        logger.info("=" * 60)
        logger.info("FIDE Data Update Process Completed Successfully!")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        logger.error("=" * 60)
        logger.error("FIDE Data Update Process FAILED")
        logger.error("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
