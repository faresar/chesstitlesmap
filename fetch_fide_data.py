#!/usr/bin/env python3
"""
FIDE Chess Titles Data Fetcher
Downloads and processes FIDE rating data to track titled players by country.
Includes rank tracking, monthly changes, and auto-update metadata.
"""

import requests
import zipfile
import io
import xml.etree.ElementTree as ET
import json
import logging
import os
from datetime import datetime
from collections import defaultdict

# Setup logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{log_dir}/fide_update.log'),
        logging.StreamHandler()
    ]
)

def download_fide_data():
    """Download and extract FIDE rating XML data"""
    url = 'https://ratings.fide.com/download/standard_rating_list_xml.zip'
    logging.info("="*60)
    logging.info("FIDE Data Update Process Started")
    logging.info("="*60)
    logging.info(f"Downloading FIDE data from {url}")

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    logging.info(f"Downloaded {len(response.content)} bytes")

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        xml_filename = zip_file.namelist()[0]
        os.makedirs('temp', exist_ok=True)
        zip_file.extractall('temp')
        xml_path = f'temp/{xml_filename}'
        logging.info(f"Extracted XML file: {xml_path}")
        return xml_path

def load_previous_data():
    """Load previous data for comparison"""
    try:
        with open('titled_players_by_country.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            previous_data = {item['Country']: item for item in data['titled_players_by_country']}
            metadata = data.get('metadata', {})
            logging.info("Loaded previous data for comparison")
            return previous_data, metadata
    except FileNotFoundError:
        logging.info("No previous data found - this is the first run")
        return {}, {}

def parse_xml_data(xml_path, previous_data):
    """Parse XML and extract titled players data with change tracking"""
    logging.info("Parsing XML data...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    country_data = defaultdict(lambda: {
        'Total': {'GM': 0, 'IM': 0, 'FM': 0, 'CM': 0, 'WGM': 0, 'WIM': 0, 'WFM': 0, 'WCM': 0},
        'Active': {'GM': 0, 'IM': 0, 'FM': 0, 'CM': 0, 'WGM': 0, 'WIM': 0, 'WFM': 0, 'WCM': 0},
        'Inactive': {'GM': 0, 'IM': 0, 'FM': 0, 'CM': 0, 'WGM': 0, 'WIM': 0, 'WFM': 0, 'WCM': 0}
    })

    new_gms = []
    new_wgms = []
    title_changes = defaultdict(lambda: {'added': 0, 'removed': 0})

    total_players = 0
    titled_players = 0

    for player in root.findall('player'):
        total_players += 1
        title = player.findtext('title', '').strip()
        country = player.findtext('country', 'UNK').strip()
        flag = player.findtext('flag', 'i').strip()
        name = player.findtext('name', '').strip()

        if not title or title not in ['GM', 'IM', 'FM', 'CM', 'WGM', 'WIM', 'WFM', 'WCM']:
            continue

        titled_players += 1

        is_active = (flag == 'i')

        country_data[country]['Total'][title] += 1
        if is_active:
            country_data[country]['Inactive'][title] += 1
        else:
            country_data[country]['Active'][title] += 1

        if title == 'GM':
            if country not in previous_data or previous_data[country]['Total']['GM'] < country_data[country]['Total']['GM']:
                new_gms.append({'name': name, 'country': country})

        if title == 'WGM':
            if country not in previous_data or previous_data[country]['Total']['WGM'] < country_data[country]['Total']['WGM']:
                new_wgms.append({'name': name, 'country': country})

    for country in country_data.keys():
        for title in ['GM', 'IM', 'FM', 'CM', 'WGM', 'WIM', 'WFM', 'WCM']:
            new_count = country_data[country]['Total'][title]
            old_count = previous_data.get(country, {}).get('Total', {}).get(title, 0)
            diff = new_count - old_count
            if diff > 0:
                title_changes[title]['added'] += diff
            elif diff < 0:
                title_changes[title]['removed'] += abs(diff)

    logging.info(f"Parsed {total_players} total players, kept {titled_players} titled players")

    return country_data, title_changes, new_gms, new_wgms

def calculate_rankings(country_data):
    """Calculate rankings for Open and Women categories"""
    men_ranking = []
    women_ranking = []

    for country, data in country_data.items():
        total = data['Total']
        men_ranking.append({
            'country': country,
            'GM': total['GM'],
            'IM': total['IM'],
            'FM': total['FM'],
            'CM': total['CM']
        })
        women_ranking.append({
            'country': country,
            'WGM': total['WGM'],
            'WIM': total['WIM'],
            'WFM': total['WFM'],
            'WCM': total['WCM']
        })

    men_ranking.sort(key=lambda x: (x['GM'], x['IM'], x['FM'], x['CM']), reverse=True)
    women_ranking.sort(key=lambda x: (x['WGM'], x['WIM'], x['WFM'], x['WCM']), reverse=True)

    men_ranks = {item['country']: rank + 1 for rank, item in enumerate(men_ranking) if item['GM'] or item['IM'] or item['FM'] or item['CM']}
    women_ranks = {item['country']: rank + 1 for rank, item in enumerate(women_ranking) if item['WGM'] or item['WIM'] or item['WFM'] or item['WCM']}

    return {'men': men_ranks, 'women': women_ranks}

def get_data_month_from_filename(xml_path):
    """
    Extract the data month from XML filename
    Filename format: standard_rating_list_MMYYYY.xml or similar
    """
    import re
    filename = os.path.basename(xml_path)

    # Try to extract month from filename
    # Common patterns: jan, january, 01, etc.
    month_map = {
        '01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR',
        '05': 'MAY', '06': 'JUN', '07': 'JUL', '08': 'AUG',
        '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC',
        'jan': 'JAN', 'feb': 'FEB', 'mar': 'MAR', 'apr': 'APR',
        'may': 'MAY', 'jun': 'JUN', 'jul': 'JUL', 'aug': 'AUG',
        'sep': 'SEP', 'oct': 'OCT', 'nov': 'NOV', 'dec': 'DEC'
    }

    # Try numeric month (01-12)
    match = re.search(r'\b(0[1-9]|1[0-2])\d{4}\b', filename)
    if match:
        month_num = match.group(1)
        return month_map.get(month_num, datetime.now().strftime("%b").upper())

    # Try text month
    for key, value in month_map.items():
        if key.lower() in filename.lower():
            return value

    # Fallback: use current month
    logging.warning(f"Could not extract month from filename: {filename}, using current month")
    return datetime.now().strftime("%b").upper()

def save_json_data(country_data, title_changes, new_gms, new_wgms, previous_metadata, xml_path):
    """Save data to JSON with metadata for auto-update and rank tracking"""
    logging.info("Generating JSON output...")

    output_data = []
    for country, data in sorted(country_data.items()):
        output_data.append({
            'Country': country,
            'Total': data['Total'],
            'Active': data['Active'],
            'Inactive': data['Inactive']
        })

    logging.info(f"Aggregated data for {len(output_data)} countries")

    current_rankings = calculate_rankings(country_data)
    previous_rankings_for_display = previous_metadata.get('current_rankings', {'men': {}, 'women': {}})

    # FIXED: Determine the correct month for this data
    data_month = get_data_month_from_filename(xml_path)
    logging.info(f"Data is for month: {data_month}")

    monthly_changes_list = previous_metadata.get('monthly_changes', [])

    total_added = sum(title_changes[title]['added'] for title in title_changes)
    total_removed = sum(title_changes[title]['removed'] for title in title_changes)
    net_change = total_added - total_removed

    previous_countries = set(previous_metadata.get('countries', []))
    current_countries = set(country_data.keys())
    new_countries = current_countries - previous_countries

    for country in new_countries:
        if country not in ['UNK', 'NON']:
            logging.info(f"NEW COUNTRY with titled players: {country}")

    monthly_change = {
        'month': data_month,  # Use extracted month, not current month
        'changes': {
            'total': net_change,
            'GM': title_changes['GM']['added'] - title_changes['GM']['removed'],
            'IM': title_changes['IM']['added'] - title_changes['IM']['removed'],
            'FM': title_changes['FM']['added'] - title_changes['FM']['removed'],
            'CM': title_changes['CM']['added'] - title_changes['CM']['removed'],
            'WGM': title_changes['WGM']['added'] - title_changes['WGM']['removed'],
            'WIM': title_changes['WIM']['added'] - title_changes['WIM']['removed'],
            'WFM': title_changes['WFM']['added'] - title_changes['WFM']['removed'],
            'WCM': title_changes['WCM']['added'] - title_changes['WCM']['removed']
        }
    }

    # Update or append monthly change
    month_exists = False
    for i, month_data in enumerate(monthly_changes_list):
        if month_data['month'] == monthly_change['month']:
            monthly_changes_list[i] = monthly_change
            month_exists = True
            break

    if not month_exists:
        monthly_changes_list.append(monthly_change)

    logging.info(f"Monthly changes for {data_month}: +{total_added}, -{total_removed}, net: {net_change}")
    for title in ['GM', 'IM', 'FM', 'CM', 'WIM', 'WFM', 'WCM']:
        added = title_changes[title]['added']
        removed = title_changes[title]['removed']
        if added > 0 or removed > 0:
            logging.info(f"  {title}: +{added}, -{removed}")

    total_gms = sum(data['Total']['GM'] for data in country_data.values())
    total_wgms = sum(data['Total']['WGM'] for data in country_data.values())
    logging.info(f"Total worldwide: {total_gms} GMs, {total_wgms} WGMs")

    current_date = datetime.now().strftime("%B %d, %Y")
    metadata = {
        'last_updated': current_date,
        'current_rankings': current_rankings,
        'previous_rankings': previous_rankings_for_display,
        'monthly_changes': monthly_changes_list,
        'countries': list(current_countries),
        'new_gms': new_gms[:10] if new_gms else [],
        'new_wgms': new_wgms[:10] if new_wgms else [],
        'total_gms': total_gms,
        'total_wgms': total_wgms
    }

    final_output = {
        'titled_players_by_country': output_data,
        'metadata': metadata
    }

    with open('titled_players_by_country.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    logging.info("JSON file saved successfully: titled_players_by_country.json")
    logging.info(f"Metadata saved: {current_date}")

    return current_date

def main():
    """Main execution function"""
    try:
        previous_data, previous_metadata = load_previous_data()

        logging.info("Processing new data...")

        xml_path = download_fide_data()

        country_data, title_changes, new_gms, new_wgms = parse_xml_data(xml_path, previous_data)

        last_updated = save_json_data(country_data, title_changes, new_gms, new_wgms, previous_metadata, xml_path)

        logging.info("="*60)
        logging.info("FIDE Data Update Process Completed Successfully!")
        logging.info("="*60)

    except Exception as e:
        logging.error(f"Error during update process: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
