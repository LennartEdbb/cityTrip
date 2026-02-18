<<<<<<< HEAD
<template>
  <div class="page">
    <div ref="mapEl" class="map"></div>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const mapEl = ref(null);
let map;

// JSON wie in deinem Beispiel (hier direkt im View)
const locations = [
  { label: "DBB", name: "DBB-Detmold", address: "Elisabethstraße 86, 32756 Detmold" },
  { label: "Cafe", name: "Cafe Mix", address: "Meierstraße 12, 32756 Detmold" }
];

function createBadge(label) {
  return L.divIcon({
    className: "marker-badge",
    html: `<div class="badge">${escapeHtml(label)}</div>`,
    iconSize: [38, 38],
    iconAnchor: [19, 38],
    popupAnchor: [0, -34]
  });
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function geocode(address) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
    address
  )}&limit=1`;

  const res = await fetch(url, { headers: { Accept: "application/json" } });
  if (!res.ok) return null;

  const data = await res.json();
  if (Array.isArray(data) && data.length > 0) {
    return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
  }
  return null;
}

async function loadMarkers() {
  const bounds = [];

  for (let i = 0; i < locations.length; i++) {
    if (i > 0) await sleep(1000); // Rate limit wie im Original

    const loc = locations[i];
    const coords = await geocode(loc.address);

    if (coords) {
      L.marker(coords, { icon: createBadge(loc.label) })
        .addTo(map)
        .bindPopup(`<b>${escapeHtml(loc.name)}</b><br>${escapeHtml(loc.address)}`);

      bounds.push(coords);
    }
  }

  if (bounds.length) {
    map.fitBounds(bounds, { padding: [30, 30] });
  }
}

function escapeHtml(str) {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

onMounted(async () => {
  map = L.map(mapEl.value).setView([51.5, 10.0], 6);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 20,
    attribution: "&copy; OpenStreetMap contributors &copy; CARTO"
  }).addTo(map);

  await loadMarkers();
});

onBeforeUnmount(() => {
  if (map) map.remove();
});
</script>

<style scoped>
.page {
  margin: 0;
  font-family: system-ui, sans-serif;
  background: #f4f6f8;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.map {
  width: 90%;
  height: 85vh;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.2);
}

:deep(.marker-badge .badge) {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  background: linear-gradient(135deg, #00c6ff, #0072ff);
  color: white;
  font-weight: 700;
  display: grid;
  place-items: center;
  font-size: 14px;
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
  border: 2px solid white;
}
</style>

=======
<template>
  <main>
    <TheWelcome />
  </main>
</template>

>>>>>>> 84f4661a7530266dcadcf81824100c8aeba3b2b4