/**
 * Map Container Helper
 * Creates a Leaflet map with coordinate and zoom display
 * 
 * Usage:
 *   const mapHelper = createMapContainer('map', { lat: 52.52, lng: 13.405, zoom: 13 });
 *   mapHelper.setView(lat, lng, zoom);
 *   mapHelper.setMarker(lat, lng);
 */

function createMapContainer(mapId, options = {}) {
    const lang = document.documentElement.lang || 'en';
    const defaultLat = options.lat || 52.520008;
    const defaultLng = options.lng || 13.404954;
    const defaultZoom = options.zoom || 13;
    const interactive = options.interactive !== false;
    const showMarker = options.showMarker !== false;
    
    // Initialize map
    const mapOptions = {
        scrollWheelZoom: interactive,
        dragging: interactive,
        touchZoom: interactive,
        doubleClickZoom: interactive,
        boxZoom: interactive,
        keyboard: interactive,
        zoomControl: interactive
    };
    
    const map = L.map(mapId, mapOptions).setView([defaultLat, defaultLng], defaultZoom);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    let marker = showMarker ? L.marker([defaultLat, defaultLng]).addTo(map) : null;
    
    const coordsEl = document.getElementById(`${mapId}-coords`);
    const zoomEl = document.getElementById(`${mapId}-zoom`);
    
    function updateInfo() {
        const center = map.getCenter();
        const zoom = map.getZoom();
        
        if (coordsEl) {
            const latLabel = lang === 'de' ? 'Lat' : 'Lat';
            const lngLabel = lang === 'de' ? 'Lon' : 'Lon';
            coordsEl.textContent = `${latLabel}: ${center.lat.toFixed(6)}° | ${lngLabel}: ${center.lng.toFixed(6)}°`;
        }
        
        if (zoomEl) {
            zoomEl.textContent = `Zoom: ${zoom}`;
        }
    }
    
    // Update info on map events
    map.on('moveend', updateInfo);
    map.on('zoomend', updateInfo);
    
    // Initial update
    updateInfo();
    
    return {
        map: map,
        marker: marker,
        
        setView: function(lat, lng, zoom) {
            map.setView([lat, lng], zoom || map.getZoom());
            updateInfo();
        },
        
        setMarker: function(lat, lng) {
            if (marker) {
                marker.setLatLng([lat, lng]);
            } else {
                marker = L.marker([lat, lng]).addTo(map);
            }
        },
        
        removeMarker: function() {
            if (marker) {
                map.removeLayer(marker);
                marker = null;
            }
        },
        
        getCenter: function() {
            const center = map.getCenter();
            return { lat: center.lat, lng: center.lng };
        },
        
        getZoom: function() {
            return map.getZoom();
        },
        
        invalidateSize: function() {
            map.invalidateSize();
        },
        
        on: function(event, callback) {
            map.on(event, callback);
        }
    };
}
