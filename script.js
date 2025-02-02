"use strict";
let titledPlayersData = {};
let currentFilter = 'both';
let currentHighlight = 'none';

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("label-highlight-none").classList.add('active');
});

function updateWorldwideNumbers() {
  let gmCount = 0, wgmCount = 0, imCount = 0, wimCount = 0, fmCount = 0, wfmCount = 0, cmCount = 0, wcmCount = 0;
  Object.values(titledPlayersData).forEach(countryData => {
    let source = currentFilter === 'active' ? countryData.Active 
                 : currentFilter === 'inactive' ? countryData.Inactive 
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
  document.getElementById('gm-count').textContent = gmCount;
  document.getElementById('wgm-count').textContent = wgmCount;
  document.getElementById('im-count').textContent = imCount;
  document.getElementById('wim-count').textContent = wimCount;
  document.getElementById('fm-count').textContent = fmCount;
  document.getElementById('wfm-count').textContent = wfmCount;
  document.getElementById('cm-count').textContent = cmCount;
  document.getElementById('wcm-count').textContent = wcmCount;
}

function updateTopCountries() {
  let menData = [];
  let womenData = [];
  Object.keys(titledPlayersData).forEach(countryCode => {
    const data = titledPlayersData[countryCode];
    const source = currentFilter === 'active' ? data.Active 
                 : currentFilter === 'inactive' ? data.Inactive 
                 : data.Total;
    menData.push({ code: countryCode, GM: source?.GM || 0, IM: source?.IM || 0, FM: source?.FM || 0, CM: source?.CM || 0 });
    womenData.push({ code: countryCode, WGM: source?.WGM || 0, WIM: source?.WIM || 0, WFM: source?.WFM || 0, WCM: source?.WCM || 0 });
  });
  
  menData.sort((a, b) => b.GM - a.GM || b.IM - a.IM || b.FM - a.FM || b.CM - a.CM);
  const menTbody = document.querySelector('#top-countries-men tbody');
  menTbody.innerHTML = '';
  menData.forEach((item, index) => {
    if (item.GM || item.IM || item.FM || item.CM) {
      const flagUrl = (item.code === "FID") ? "Fidelogo.png" : `https://ratings.fide.com/svg/${item.code}.svg`;
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${index+1}</td>
                      <td><img src="${flagUrl}" class="flag" alt="${item.code} Flag"> ${item.code}</td>
                      <td>${item.GM}</td>
                      <td>${item.IM}</td>
                      <td>${item.FM}</td>
                      <td>${item.CM}</td>`;
      menTbody.appendChild(tr);
    }
  });
  
  const womenTbody = document.querySelector('#top-countries-women tbody');
  womenTbody.innerHTML = '';
  womenData.forEach((item, index) => {
    if (item.WGM || item.WIM || item.WFM || item.WCM) {
      const flagUrl = (item.code === "FID") ? "Fidelogo.png" : `https://ratings.fide.com/svg/${item.code}.svg`;
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${index+1}</td>
                      <td><img src="${flagUrl}" class="flag" alt="${item.code} Flag"> ${item.code}</td>
                      <td>${item.WGM}</td>
                      <td>${item.WIM}</td>
                      <td>${item.WFM}</td>
                      <td>${item.WCM}</td>`;
      womenTbody.appendChild(tr);
    }
  });
}

fetch('titled_players_by_country.json')
  .then(response => response.json())
  .then(data => {
    data.titled_players_by_country.forEach(item => {
      titledPlayersData[item.Country] = item;
    });
    updateWorldwideNumbers();
    updateTopCountries();
  })
  .catch(error => { console.error('Error fetching titled players data:', error); });

fetch('world_fide.svg')
  .then(response => response.text())
  .then(svgContent => {
    document.getElementById('svg-container').innerHTML += svgContent.trim();
    initializeMap();
  });

function initializeMap() {
  const svgContainer = document.getElementById('svg-container');
  const svgElement = svgContainer.querySelector('svg');
  const infoBox = document.getElementById("info-box");
  let selectedCountry = null;

  const panZoom = svgPanZoom(svgElement, {
    zoomEnabled: true,
    controlIconsEnabled: false,
    fit: true,
    center: true,
    minZoom: 1,
    maxZoom: 72,
    zoomScaleSensitivity: 0.2,
  });
  panZoom.disableDblClickZoom();

  document.getElementById("zoom-in").addEventListener("click", () => panZoom.zoomIn());
  document.getElementById("zoom-out").addEventListener("click", () => panZoom.zoomOut());
  document.getElementById("zoom-reset").addEventListener("click", () => {
    panZoom.reset();
    panZoom.resize().fit().center();
  });

  document.getElementById("filter-both").addEventListener("click", () => {
    currentFilter = 'both';
    updateFilterButtons();
    updateHighlight();
    updateWorldwideNumbers();
    updateTopCountries();
  });
  document.getElementById("filter-active").addEventListener("click", () => {
    currentFilter = 'active';
    updateFilterButtons();
    updateHighlight();
    updateWorldwideNumbers();
    updateTopCountries();
  });
  document.getElementById("filter-inactive").addEventListener("click", () => {
    currentFilter = 'inactive';
    updateFilterButtons();
    updateHighlight();
    updateWorldwideNumbers();
    updateTopCountries();
  });

  function updateFilterButtons() {
    document.getElementById("filter-both").classList.toggle("active", currentFilter === 'both');
    document.getElementById("filter-active").classList.toggle("active", currentFilter === 'active');
    document.getElementById("filter-inactive").classList.toggle("active", currentFilter === 'inactive');
  }

  const highlightCheckboxes = document.querySelectorAll('.highlight-titles-buttons input[type="checkbox"]');
  highlightCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      document.querySelectorAll('.highlight-titles-buttons label').forEach(label => label.classList.remove('active'));
      if (checkbox.checked) {
        checkbox.parentElement.classList.add('active');
        currentHighlight = checkbox.value;
        highlightCheckboxes.forEach(cb => {
          if (cb !== checkbox) {
            cb.checked = false;
            cb.parentElement.classList.remove('active');
          }
        });
      } else {
        currentHighlight = 'none';
        document.getElementById("highlight-none").checked = true;
        document.getElementById("label-highlight-none").classList.add('active');
      }
      updateHighlight();
    });
  });

  function updateHighlight() {
    const paths = svgElement.querySelectorAll("path");
    paths.forEach(path => {
      path.classList.remove('highlighted');
      const countryCode = path.id;
      const countryData = titledPlayersData[countryCode] || {};
      if (currentHighlight !== 'none') {
        let source = currentFilter === 'active' ? countryData.Active 
                   : currentFilter === 'inactive' ? countryData.Inactive 
                   : countryData.Total;
        const count = source?.[currentHighlight] || 0;
        if (count > 0) path.classList.add('highlighted');
      }
    });
  }

  if (!document.getElementById("info-box")) {
    const div = document.createElement("div");
    div.id = "info-box";
    div.className = "info-box";
    document.body.appendChild(div);
  }

  function showInfoBox(countryCode, x, y) {
    const flagUrl = (countryCode === "FID") ? "Fidelogo.png" : `https://ratings.fide.com/svg/${countryCode}.svg`;
    const countryData = titledPlayersData[countryCode] || {};
    let source = currentFilter === 'active' ? countryData.Active 
               : currentFilter === 'inactive' ? countryData.Inactive 
               : countryData.Total;
    const gmCount = source?.GM || 0,
          wgmCount = source?.WGM || 0,
          imCount = source?.IM || 0,
          wimCount = source?.WIM || 0,
          fmCount = source?.FM || 0,
          wfmCount = source?.WFM || 0,
          cmCount = source?.CM || 0,
          wcmCount = source?.WCM || 0;
    infoBox.innerHTML = `
      <img src="${flagUrl}" alt="${countryCode} Flag" class="flag">
      <a href="https://ratings.fide.com/rankings.phtml?country=${countryCode}" target="_blank">${countryCode}</a><br>
      <b>GM:</b> ${gmCount} | <b>WGM:</b> ${wgmCount}<br>
      <b>IM:</b> ${imCount} | <b>WIM:</b> ${wimCount}<br>
      <b>FM:</b> ${fmCount} | <b>WFM:</b> ${wfmCount}<br>
      <b>CM:</b> ${cmCount} | <b>WCM:</b> ${wcmCount}
    `;
    infoBox.classList.add('visible');
    const boxHeight = infoBox.offsetHeight || 50;
    const boxWidth = infoBox.offsetWidth || 100;
    infoBox.style.left = `${x - boxWidth/2}px`;
    infoBox.style.top = `${y - boxHeight}px`;
  }

  function hideInfoBox() {
    if (selectedCountry) {
      document.querySelector(`path[id="${selectedCountry}"]`).classList.remove('selected');
      selectedCountry = null;
    }
    infoBox.classList.remove('visible');
  }

  const paths = svgElement.querySelectorAll("path");
  paths.forEach(path => {
    path.addEventListener("mouseenter", (e) => {
      if (!selectedCountry) showInfoBox(path.id, e.clientX, e.clientY);
    });
    path.addEventListener("mouseleave", () => {
      if (!selectedCountry && !infoBox.matches(':hover')) hideInfoBox();
    });
    path.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1) {
        if (selectedCountry)
          document.querySelector(`path[id="${selectedCountry}"]`).classList.remove('selected');
        selectedCountry = path.id;
        path.classList.add('selected');
        showInfoBox(path.id, e.touches[0].clientX, e.touches[0].clientY);
      }
    });
  });
  
  infoBox.addEventListener('mouseenter', () => { infoBox.classList.add('visible'); });
  infoBox.addEventListener('mouseleave', () => { if (!selectedCountry) hideInfoBox(); });
  document.addEventListener("touchstart", (e) => {
    if (!infoBox.contains(e.target) && !Array.from(paths).some(path => path.contains(e.target))) hideInfoBox();
  });
  
  window.addEventListener('resize', () => { panZoom.resize().fit().center(); });
  let initialDistance = null, initialScale = 1;
  svgContainer.addEventListener("touchstart", (e) => {
    if (e.touches.length === 2) {
      initialDistance = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      initialScale = panZoom.getZoom();
    }
  });
  svgContainer.addEventListener("touchmove", (e) => {
    if (e.touches.length === 2 && initialDistance !== null) {
      e.preventDefault();
      const currentDistance = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      const scale = (currentDistance / initialDistance) * initialScale;
      const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      const svgPoint = svgElement.createSVGPoint();
      svgPoint.x = centerX;
      svgPoint.y = centerY;
      const transformedPoint = svgPoint.matrixTransform(svgElement.getScreenCTM().inverse());
      panZoom.zoomAtPoint(scale, transformedPoint);
    }
  });
  svgContainer.addEventListener("touchend", () => { initialDistance = null; });
}
