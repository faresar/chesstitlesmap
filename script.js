"use strict";

// Object to hold titled players data per country (populated from JSON)
let titledPlayersData = {};

// Current filter for statistics and tables: "both", "active", "inactive"
let currentFilter = 'both';

// Current highlight selection (e.g., "none", "GM", "IM", etc.)
let currentHighlight = 'none';

// Current zoom scale for the SVG map; initial scale is 1 (no zoom)
let currentScale = 1;

// When the DOM is fully loaded, initialize defaults and load JSON data
window.addEventListener("DOMContentLoaded", () => {
  // Set the default highlight label to "None/Reset"
  document.getElementById("label-highlight-none").classList.add('active');

  // Fetch and load the titled players data JSON
  fetch('titled_players_by_country.json')
    .then(response => response.json())
    .then(data => {
      // Build the data object using country codes as keys
      titledPlayersData = {};
      data.titled_players_by_country.forEach(item => {
        titledPlayersData[item.Country] = item;
      });
      // Update worldwide statistics and the Top Countries tables
      updateWorldwideNumbers();
      updateTopCountries();
    })
    .catch(err => console.error("Error loading JSON data:", err));

  // Initialize zoom control functionality
  setupZoomControls();
});

// Function to update worldwide statistics from the data set
function updateWorldwideNumbers() {
  let gmCount = 0, wgmCount = 0, imCount = 0, wimCount = 0, fmCount = 0, wfmCount = 0, cmCount = 0, wcmCount = 0;
  
  // Loop over each country in the data set
  Object.values(titledPlayersData).forEach(countryData => {
    // Choose the appropriate source based on the current filter setting
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
  
  // Update the DOM elements with the computed values
  document.getElementById('gm-count').textContent = gmCount;
  document.getElementById('wgm-count').textContent = wgmCount;
  document.getElementById('im-count').textContent = imCount;
  document.getElementById('wim-count').textContent = wimCount;
  document.getElementById('fm-count').textContent = fmCount;
  document.getElementById('wfm-count').textContent = wfmCount;
  document.getElementById('cm-count').textContent = cmCount;
  document.getElementById('wcm-count').textContent = wcmCount;
}

// Function to update the Top Countries tables for both men and women
function updateTopCountries() {
  let menData = [];
  let womenData = [];
  
  // Process each country's data
  Object.keys(titledPlayersData).forEach(countryCode => {
    const data = titledPlayersData[countryCode];
    // Select data based on the current filter (Active/Inactive/Total)
    const source = currentFilter === 'active'
      ? data.Active
      : currentFilter === 'inactive'
      ? data.Inactive
      : data.Total;
      
    // Prepare men's data with GM, IM, FM, CM counts
    menData.push({
      code: countryCode,
      GM: source?.GM || 0,
      IM: source?.IM || 0,
      FM: source?.FM || 0,
      CM: source?.CM || 0
    });
    
    // Prepare women's data with WGM, WIM, WFM, WCM counts
    womenData.push({
      code: countryCode,
      WGM: source?.WGM || 0,
      WIM: source?.WIM || 0,
      WFM: source?.WFM || 0,
      WCM: source?.WCM || 0
    });
  });
  
  // Sort men's data in descending order (priority: GM then IM then FM then CM)
  menData.sort((a, b) => b.GM - a.GM || b.IM - a.IM || b.FM - a.FM || b.CM - a.CM);
  // Sort women's data in descending order (priority: WGM then WIM then WFM then WCM)
  womenData.sort((a, b) => b.WGM - a.WGM || b.WIM - a.WIM || b.WFM - a.WFM || b.WCM - a.WCM);
  
  // Populate Men's table
  const menTbody = document.querySelector('#top-countries-men tbody');
  menTbody.innerHTML = '';
  menData.forEach((item, index) => {
    if (item.GM || item.IM || item.FM || item.CM) {
      // Determine flag image URL; for special "FID" code use local image
      const flagUrl = (item.code === "FID") ? "Fidelogo.png" : `https://ratings.fide.com/svg/${item.code}.svg`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td><img class="flag" src="${flagUrl}" alt="${item.code} flag"> ${item.code}</td>
        <td>${item.GM}</td>
        <td>${item.IM}</td>
        <td>${item.FM}</td>
        <td>${item.CM}</td>
      `;
      menTbody.appendChild(tr);
    }
  });
  
  // Populate Women's table
  const womenTbody = document.querySelector('#top-countries-women tbody');
  womenTbody.innerHTML = '';
  womenData.forEach((item, index) => {
    if (item.WGM || item.WIM || item.WFM || item.WCM) {
      const flagUrl = (item.code === "FID") ? "Fidelogo.png" : `https://ratings.fide.com/svg/${item.code}.svg`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td><img class="flag" src="${flagUrl}" alt="${item.code} flag"> ${item.code}</td>
        <td>${item.WGM}</td>
        <td>${item.WIM}</td>
        <td>${item.WFM}</td>
        <td>${item.WCM}</td>
      `;
      womenTbody.appendChild(tr);
    }
  });
}

// Function to setup the zoom controls for the SVG map
function setupZoomControls() {
  const zoomInButton = document.getElementById('zoom-in');
  const zoomOutButton = document.getElementById('zoom-out');
  const resetZoomButton = document.getElementById('reset-zoom');
  const svgContainer = document.getElementById('svg-container');
  
  // Zoom In: increase scale by a factor (e.g., 1.2)
  zoomInButton.addEventListener('click', () => {
    currentScale *= 1.2;
    svgContainer.style.transform = `scale(${currentScale})`;
  });
  
  // Zoom Out: decrease the scale by the same factor
  zoomOutButton.addEventListener('click', () => {
    currentScale /= 1.2;
    svgContainer.style.transform = `scale(${currentScale})`;
  });
  
  // Reset Zoom: set scale back to 1 (original size)
  resetZoomButton.addEventListener('click', () => {
    currentScale = 1;
    svgContainer.style.transform = `scale(1)`;
  });
}
