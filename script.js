// Globe animation
function initGlobe() {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('globe').appendChild(renderer.domElement);

    const geometry = new THREE.SphereGeometry(5, 32, 32);
    const texture = new THREE.TextureLoader().load('path/to/earth-texture.jpg');
    const material = new THREE.MeshBasicMaterial({ map: texture });
    const globe = new THREE.Mesh(geometry, material);
    scene.add(globe);

    camera.position.z = 10;

    function animate() {
        requestAnimationFrame(animate);
        globe.rotation.y += 0.005;
        renderer.render(scene, camera);
    }
    animate();
}

// Circular menu
const menuButton = document.querySelector('.menu-button');
const menuItems = document.querySelector('.menu-items');

menuButton.addEventListener('click', () => {
    menuItems.style.display = menuItems.style.display === 'block' ? 'none' : 'block';
    menuButton.style.transform = menuButton.style.transform === 'rotate(45deg)' ? 'rotate(0deg)' : 'rotate(45deg)';
});

// Map interaction
function initMap() {
    // Fetch and insert SVG map
    fetch('https://raw.githubusercontent.com/mledoze/countries/master/countries.svg')
        .then(response => response.text())
        .then(svgContent => {
            document.getElementById('map-container').innerHTML = svgContent;
            addMapInteractivity();
        });
}

function addMapInteractivity() {
    const countries = document.querySelectorAll('#map-container path');
    countries.forEach(country => {
        country.addEventListener('mouseover', showTooltip);
        country.addEventListener('mouseout', hideTooltip);
        country.addEventListener('click', showCountryInfo);
    });
}

function showTooltip(event) {
    // Implement tooltip logic
}

function hideTooltip() {
    // Implement hide tooltip logic
}

function showCountryInfo(event) {
    const countryInfo = document.getElementById('country-info');
    countryInfo.style.transform = 'translateX(0)';
    // Fetch and display country-specific chess data
}

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    initGlobe();
    initMap();
});
