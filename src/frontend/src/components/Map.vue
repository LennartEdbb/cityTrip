<template>
  <div class="map-wrap">
    <div ref="mapEl" class="map"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from "vue"
import L from "leaflet"
import "leaflet/dist/leaflet.css"

type LocationItem = {
  label: string
  name: string
  address: string
}

const mapEl = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null

function createBadge(label: string) {
  return L.divIcon({
    className: "marker-badge",
    html: `<div class="badge">${escapeHtml(label)}</div>`,
    iconSize: [38, 38],
    iconAnchor: [19, 38],
    popupAnchor: [0, -34],
  })
}

function escapeHtml(s: string) {
  return String(s).replace(/[&<>"']/g, (c) => {
    const m: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    }
    return m[c] ?? c
  })
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

async function geocode(address: string): Promise<[number, number] | null> {
  const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
    address
  )}&limit=1`

  const res = await fetch(url, { headers: { Accept: "application/json" } })
  if (!res.ok) return null

  const data = await res.json()
  if (Array.isArray(data) && data.length > 0) {
    const lat = parseFloat(data[0].lat)
    const lon = parseFloat(data[0].lon)
    if (Number.isFinite(lat) && Number.isFinite(lon)) return [lat, lon]
  }
  return null
}

async function loadMarkers() {
  const res = await fetch("/addresses.json", { cache: "no-store" })
  if (!res.ok) {
    console.error("addresses.json nicht gefunden. Lege sie in /public/addresses.json ab.")
    return
  }

  const locations = (await res.json()) as LocationItem[]
  const bounds = L.latLngBounds([])

  for (let i = 0; i < locations.length; i++) {
    const loc = locations[i]
    if (!loc?.address) continue

    // 1 Sek Pause -> freundlich zu Nominatim
    if (i > 0) await sleep(1000)

    const coords = await geocode(loc.address)
    if (!coords) {
      console.warn("Geocoding fehlgeschlagen:", loc.address)
      continue
    }

    const marker = L.marker(coords, { icon: createBadge(loc.label) })
      .addTo(map!)
      .bindPopup(`<b>${escapeHtml(loc.name)}</b><br>${escapeHtml(loc.address)}`)

    bounds.extend(marker.getLatLng())
  }

  if (bounds.isValid()) {
    map!.fitBounds(bounds, { padding: [40, 40] })
  }
}

onMounted(async () => {
  if (!mapEl.value) return

  map = L.map(mapEl.value, { zoomControl: false }).setView([51.5, 10.0], 6)

  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 20,
    attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
  }).addTo(map)

  L.control.zoom({ position: "bottomright" }).addTo(map)

  await loadMarkers()
})

onBeforeUnmount(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
.map-wrap {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f4f6f8;
  margin: 0;
}

.map {
  width: 90%;
  height: 85vh;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.2);
}

.marker-badge .badge {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  background: linear-gradient(135deg, #00c6ff, #0072ff);
  color: rgb(255, 2, 2);
  font-weight: 700;
  display: grid;
  place-items: center;
  font-size: 14px;
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.2);
  border: 2px solid white;
}
</style>
