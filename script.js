"use strict";

// Object to hold titled players data per country.
// Data will be populated from an external source.
let titledPlayersData = {};

// Stores the current filter: 'both', 'active', or 'inactive'
let currentFilter = 'both';

// Stores the current highlight option for map titles.
let currentHighlight = 'none';

// When the DOM content is loaded, initialize UI defaults.
window.addEventListener("DOMContentLoaded", () => {
  // Set the default active highlight label to "None/Reset".
  document.getElementById("label-highlight-none").classList.add('active');
  // Additional initialization (if needed) goes here.
});

// Updates worldwide counts for each chess title.
function updateWorldwideNumbers() {
  let gmCount = 0,
      wgmCount = 0,
      imCount = 0,
      wimCount = 0,
      fmCount = 0,
      wfmCount = 0,
      cmCount = 0,
      wcmCount = 0;

  // Loop through each country's data.
  Object.values(titledPlayersData).forEach(countryData => {
    // Select data based on current filter.
    let source = currentFilter === 'active'
      ? countryData.Active
      : currentFilter === 'inactive'
      ? countryData.Inactive
      : countryData.Total;
      
    gmCount += source?.GM || 0;
    wgmCount += source?.WGM || 0;
    imCount += source?.IM || 0;
    wimCount += source?.WIM || 0;
    fmCount += source?.FM || 0;
    wfmCount += source?.WFM || 0;
    cmCount += source?.CM || 0;
    wcmCount += source?.WCM || 0;
  });

  // Update the DOM elements with the calculated counts.
  document.getElementById('gm-count').textContent = gmCount;
  document.getElementById('wgm-count').textContent = wgmCount;
  document.getElementById('im-count').textContent = imCount;
  document.getElementById('wim-count').textContent = wimCount;
  document.getElementById('fm-count').textContent = fmCount;
  document.getElementById('wfm-count').textContent = wfmCount;
  document.getElementById('cm-count').textContent = cmCount;
  document.getElementById('wcm-count').textContent = wcmCount;
}

// Updates both the men's and women's Top Countries tables.
function updateTopCountries() {
  let menData = [];
  let womenData = [];

  // Process each country code in our data set.
  Object.keys(titledPlayersData).forEach(countryCode => {
    const data = titledPlayersData[countryCode];
    // Choose data based on current filter.
    const source = currentFilter === 'active'
      ? data.Active
      : currentFilter === 'inactive'
      ? data.Inactive
      : data.Total;
      
    menData.push({
      code: countryCode,
      GM: source?.GM || 0,
      IM: source?.IM || 0,
      FM: source?.FM || 0,
      CM: source?.CM || 0
    });
    womenData.push({
      code: countryCode,
      WGM: source?.WGM || 0,
      WIM: source?.WIM || 0,
      WFM: source?.WFM || 0,
      WCM: source?.WCM || 0
    });
  });

  // Sort men's data (descending order: GM, then IM, then FM, then CM).
  menData.sort((a, b) => b.GM - a.GM || b.IM - a.IM || b.FM - a.FM || b.CM - a.CM);
  
  // Sort women's data (descending order: WGM, then WIM, then WFM, then WCM).
  womenData.sort((a, b) => b.WGM - a.WGM || b.WIM - a.WIM || b.WFM - a.WFM || b.WCM - a.WCM);

  // Populate Men's table.
  const menTbody = document.querySelector('#top-countries-men tbody');
  menTbody.innerHTML = '';
  menData.forEach((item, index) => {
    if (item.GM || item.IM || item.FM || item.CM) {
      // Determine flag image URL.
      const flagUrl = item.code === "FID" ? "Fidelogo.png" : `https://ratings.fide.com/svg/${item.code}.svg`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td><img class="flag" src="${flagUrl}" alt="${item.code} flag">${item.code}</td>
        <td>${item.GM}</td>
        <td>${item.IM}</td>
        <td>${item.FM}</td>
        <td>${item.CM}</td>
      `;
      menTbody.appendChild(tr);
    }
  });

  // Populate Women's table using the updated ranking logic.
  const womenTbody = document.querySelector('#top-countries-women tbody');
  womenTbody.innerHTML = '';
  womenData.forEach((item, index) => {
    if (item.WGM || item.WIM || item.WFM || item.WCM) {
      // Determine flag image URL.
      const flagUrl = item.code === "FID" ? "Fidelogo.png" : `https://ratings.fide.com/svg/${item.code}.svg`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td><img class="flag" src="${flagUrl}" alt="${item.code} flag">${item.code}</td>
        <td>${item.WGM}</td>
        <td>${item.WIM}</td>
        <td>${item.WFM}</td>
        <td>${item.WCM}</td>
      `;
      womenTbody.appendChild(tr);
    }
  });
}

// Function to initialize zoom control buttons.
function setupZoomControls() {
  const zoomInButton = document.getElementById('zoom-in');
  const zoomOutButton = document.getElementById('zoom-out');
  const resetZoomButton = document.getElementById('reset-zoom');

  // Zoom In functionality.
  zoomInButton.addEventListener('click', () => {
    // TODO: Implement zoom in functionality.
  });
  
  // Zoom Out functionality.
  zoomOutButton.addEventListener('click', () => {
    // TODO: Implement zoom out functionality.
  });
  
  // Reset Zoom functionality.
  resetZoomButton.addEventListener('click', () => {
    // TODO: Implement reset zoom functionality.
  });
}

// Initialize zoom controls on page load.
setupZoomControls();
