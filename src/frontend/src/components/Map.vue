<template>
  <div class="map-shell">
    <!-- Top header -->
    <div class="top-ui">
      <div class="top-row">
        <button class="icon-btn" aria-label="Menu">
          <svg viewBox="0 0 24 24" fill="none">
            <path
              d="M4 7h16M4 12h16M4 17h10"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </button>

        <div class="title">VENUES NEAR YOU</div>
        <div class="spacer" aria-hidden="true" />
      </div>
    </div>

    <!-- Map -->
    <div ref="mapEl" class="map" />

    <!-- Cards -->
    <div class="sheet" v-if="sortedVenues.length">
      <div class="sheet-handle" />
      <div class="cards">
        <button
          v-for="(v, idx) in sortedVenues"
          :key="v.id"
          class="card"
          type="button"
          @click="focusVenue(v)"
        >
          <div class="card-top">
            <div class="card-title">
              <span class="rank">{{ idx + 1 }}.</span>
              <span class="name">{{ v.name }}</span>
            </div>

            <div class="distance">
              <span class="pin">📍</span>
              <span>{{ v.distanceText ?? "—" }}</span>
            </div>
          </div>

          <div class="card-mid" v-if="typeof v.rating === 'number'">
            <span class="stars">{{ stars(v.rating) }}</span>
            <span class="reviews" v-if="typeof v.reviews === 'number'">
              {{ v.reviews }} reviews
            </span>
          </div>

          <div class="tag-row" v-if="v.tags?.length">
            <span class="tag" v-for="t in v.tags" :key="t">{{ t }}</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Bottom nav -->
    <div class="bottom-nav">
      <button class="nav-item">
        <span class="nav-ic">⚙️</span>
        <span>Settings</span>
      </button>

      <button class="nav-fab" aria-label="Primary action">
        <span class="fab-dot" />
        <span class="cal-ic">📅</span>
      </button>

      <button class="nav-item">
        <span class="nav-ic">📈</span>
        <span>Activity</span>
      </button>
    </div>

    <OwnLocation @location-obtained="addUserMarker" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from "vue"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import OwnLocation from "./OwnLocation.vue"

type Venue = {
  id: string
  label?: string
  name: string
  address: string
  tags?: string[]
  rating?: number
  reviews?: number

  lat?: number
  lng?: number
  distanceM?: number
  distanceText?: string
}

const mapEl = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null

let routeLine: L.Polyline | null = null
let userLatLng: L.LatLng | null = null
let userMarker: L.CircleMarker | null = null
let accuracyHalo: L.Circle | null = null

// store markers for venues
let venueMarkers = new Map<string, L.Marker>()

const venues = ref<Venue[]>([])

const sortedVenues = computed(() => {
  const list = [...venues.value]
  const hasDistances = list.some((v) => typeof v.distanceM === "number")
  if (!hasDistances) return list
  return list.sort((a, b) => (a.distanceM ?? 9e15) - (b.distanceM ?? 9e15))
})

function stars(r: number) {
  const full = Math.max(0, Math.min(5, Math.round(r)))
  return "★★★★★".slice(0, full) + "☆☆☆☆☆".slice(0, 5 - full)
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

function haversineMeters(a: L.LatLng, b: L.LatLng) {
  const R = 6371000
  const toRad = (d: number) => (d * Math.PI) / 180
  const dLat = toRad(b.lat - a.lat)
  const dLng = toRad(b.lng - a.lng)
  const lat1 = toRad(a.lat)
  const lat2 = toRad(b.lat)

  const s =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.atan2(Math.sqrt(s), Math.sqrt(1 - s))
}

function formatDistance(m: number) {
  if (!Number.isFinite(m)) return "—"
  if (m < 1000) return `${Math.round(m)}m`
  const km = m / 1000
  return `${km.toFixed(km < 10 ? 1 : 0)}km`
}

function updateDistances() {
  if (!userLatLng) return
  for (const v of venues.value) {
    if (typeof v.lat !== "number" || typeof v.lng !== "number") continue
    const d = haversineMeters(userLatLng, L.latLng(v.lat, v.lng))
    v.distanceM = d
    v.distanceText = formatDistance(d)
  }
}

/** marker = red dot + label text (no svg/image) */
function createRedDotLabelIcon(label?: string) {
  const safe = label ? escapeHtml(label) : ""
  return L.divIcon({
    className: "event-marker",
    html: `
      <div class="event-marker__wrap">
        <span class="event-marker__dot"></span>
        ${safe ? `<span class="event-marker__label">${safe}</span>` : ``}
      </div>
    `,
    iconSize: [1, 1], // size comes from CSS
    iconAnchor: [7, 7], // anchor at dot center-ish
    popupAnchor: [0, -12],
  })
}

/** Smooth simple route */
function drawRoute(from: L.LatLng, to: L.LatLng) {
  if (!map) return
  if (routeLine) map.removeLayer(routeLine)

  const mid = L.latLng((from.lat + to.lat) / 2 + 0.0006, (from.lng + to.lng) / 2 - 0.001)

  routeLine = L.polyline([from, mid, to], {
    color: "#2f5bff",
    weight: 6,
    opacity: 0.95,
    lineJoin: "round",
    lineCap: "round",
  }).addTo(map)
}

function focusVenue(v: Venue) {
  if (!map || typeof v.lat !== "number" || typeof v.lng !== "number") return
  const latlng = L.latLng(v.lat, v.lng)

  map.setView(latlng, Math.max(map.getZoom(), 16), { animate: true })

  const marker = venueMarkers.get(v.id)
  marker?.openPopup()

  if (userLatLng) drawRoute(userLatLng, latlng)
}

function clearVenueMarkers() {
  if (!map) return
  for (const [, marker] of venueMarkers) map.removeLayer(marker)
  venueMarkers.clear()
}

async function loadVenuesAndMarkers() {
  if (!map) return

  const res = await fetch("/addresses.json", { cache: "no-store" })
  if (!res.ok) {
    console.error("addresses.json not found in /public")
    return
  }

  venues.value = (await res.json()) as Venue[]

  clearVenueMarkers()

  const bounds = L.latLngBounds([])

  for (let i = 0; i < venues.value.length; i++) {
    const v = venues.value[i]
    if (!v?.address) continue

    if (i > 0) await sleep(650)

    const coords = await geocode(v.address)
    if (!coords) continue

    v.lat = coords[0]
    v.lng = coords[1]

    const popupHtml = `
      <div class="popup">
        <div class="popup-title">${escapeHtml(v.name)}</div>
        <div class="popup-sub">${escapeHtml(v.address)}</div>
      </div>
    `

    const marker = L.marker(coords, { icon: createRedDotLabelIcon(v.label) })
      .addTo(map)
      .bindPopup(popupHtml, { className: "clean-popup", closeButton: false })

    venueMarkers.set(v.id, marker)
    bounds.extend(marker.getLatLng())
  }

  updateDistances()

  if (bounds.isValid()) {
    map.fitBounds(bounds, { padding: [60, 180], maxZoom: 16 })
  }
}

function addUserMarker(position: GeolocationPosition) {
  if (!map) return

  userLatLng = L.latLng(position.coords.latitude, position.coords.longitude)

  if (userMarker) map.removeLayer(userMarker)
  if (accuracyHalo) map.removeLayer(accuracyHalo)

  accuracyHalo = L.circle(userLatLng, {
    radius: 70,
    color: "#2f5bff",
    weight: 0,
    fillColor: "#2f5bff",
    fillOpacity: 0.12,
  }).addTo(map)

  userMarker = L.circleMarker(userLatLng, {
    radius: 8,
    color: "#ffffff",
    weight: 3,
    fillColor: "#2f5bff",
    fillOpacity: 1,
  }).addTo(map)

  updateDistances()
}

function handleResize() {
  map?.invalidateSize()
}

onMounted(async () => {
  if (!mapEl.value) return

  map = L.map(mapEl.value, {
    zoomControl: false,
    attributionControl: false,
    preferCanvas: true,
  }).setView([51.5, 10.0], 6)

  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 20,
  }).addTo(map)

  L.control.zoom({ position: "bottomright" }).addTo(map)

  queueMicrotask(() => map?.invalidateSize())
  window.addEventListener("resize", handleResize, { passive: true })

  await loadVenuesAndMarkers()
})

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize)
  if (map) {
    clearVenueMarkers()
    map.remove()
    map = null
  }
})
</script>

<style scoped>
/* Fullscreen */
:global(html),
:global(body),
:global(#app) {
  height: 100%;
}

:global(body) {
  margin: 0;
  overflow: hidden;
  background: #f6f7fb;
}

.map-shell {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100dvh;
  background: #f6f7fb;
  overflow: hidden;
}

.map {
  position: absolute;
  inset: 0;
}

/* Top UI */
.top-ui {
  position: absolute;
  left: 18px;
  right: 18px;
  top: calc(18px + env(safe-area-inset-top));
  z-index: 500;
  pointer-events: none;
}

.top-row {
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  gap: 10px;
}

.title {
  text-align: center;
  font-weight: 800;
  letter-spacing: 0.12em;
  font-size: 13px;
  color: #111827;
}

.spacer {
  width: 44px;
  height: 44px;
}

.icon-btn {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.92);
  display: grid;
  place-items: center;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  pointer-events: auto;
}

.icon-btn svg {
  width: 20px;
  height: 20px;
  color: #111827;
}

/* Bottom sheet */
.sheet {
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: calc(92px + env(safe-area-inset-bottom));
  z-index: 600;
  pointer-events: none;
}

.sheet-handle {
  width: 52px;
  height: 5px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.14);
  margin: 0 auto 10px auto;
}

.cards {
  pointer-events: auto;
  display: flex;
  gap: 12px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x mandatory;
  padding-bottom: 6px;
}

.card {
  flex: 0 0 min(340px, calc(100vw - 28px));
  scroll-snap-align: start;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.96);
  border-radius: 18px;
  box-shadow: 0 20px 55px rgba(0, 0, 0, 0.12);
  padding: 14px 14px 12px 14px;
  text-align: left;
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.card-title {
  display: flex;
  gap: 6px;
  align-items: baseline;
  color: #111827;
  font-weight: 800;
}

.rank {
  color: rgba(17, 24, 39, 0.6);
}

.distance {
  font-size: 12px;
  color: rgba(17, 24, 39, 0.55);
  display: inline-flex;
  gap: 6px;
  align-items: center;
  white-space: nowrap;
}

.card-mid {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.stars {
  color: #2f5bff;
  letter-spacing: 0.12em;
}

.reviews {
  color: rgba(47, 91, 255, 0.9);
  font-weight: 700;
}

.tag-row {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 12px;
  color: rgba(17, 24, 39, 0.65);
  background: rgba(17, 24, 39, 0.06);
  border: 1px solid rgba(17, 24, 39, 0.06);
  border-radius: 999px;
  padding: 6px 10px;
}

/* Bottom nav */
.bottom-nav {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: calc(86px + env(safe-area-inset-bottom));
  z-index: 650;
  background: rgba(255, 255, 255, 0.92);
  border-top: 1px solid rgba(17, 24, 39, 0.08);
  display: grid;
  grid-template-columns: 1fr 96px 1fr;
  align-items: center;
  padding: 0 18px calc(10px + env(safe-area-inset-bottom)) 18px;
  backdrop-filter: blur(10px);
}

.nav-item {
  border: 0;
  background: transparent;
  display: grid;
  justify-items: center;
  gap: 6px;
  color: rgba(17, 24, 39, 0.65);
  font-size: 12px;
}

.nav-fab {
  width: 68px;
  height: 68px;
  border-radius: 999px;
  border: 0;
  background: #2f5bff;
  color: white;
  margin: -26px auto 0 auto;
  box-shadow: 0 22px 50px rgba(47, 91, 255, 0.35);
  position: relative;
  display: grid;
  place-items: center;
}

.fab-dot {
  position: absolute;
  right: 12px;
  top: 12px;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.95);
}

.cal-ic {
  font-size: 18px;
}

/* Leaflet controls */
:deep(.leaflet-control-container .leaflet-bottom.leaflet-right) {
  margin-bottom: calc(110px + env(safe-area-inset-bottom));
  margin-right: 14px;
}

:deep(.leaflet-bar) {
  border: 0 !important;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12) !important;
  border-radius: 14px !important;
  overflow: hidden;
}

:deep(.leaflet-bar a) {
  width: 42px !important;
  height: 42px !important;
  line-height: 42px !important;
  background: rgba(255, 255, 255, 0.92) !important;
  color: #111827 !important;
  border: 0 !important;
}

/* Clean popup */
:deep(.clean-popup .leaflet-popup-content-wrapper) {
  border-radius: 14px;
  box-shadow: 0 18px 55px rgba(0, 0, 0, 0.18);
  border: 1px solid rgba(17, 24, 39, 0.08);
}

:deep(.clean-popup .leaflet-popup-content) {
  margin: 10px 12px;
}

.popup-title {
  font-weight: 800;
  color: #111827;
  font-size: 13px;
  line-height: 1.2;
}

.popup-sub {
  margin-top: 2px;
  color: rgba(17, 24, 39, 0.6);
  font-size: 12px;
  line-height: 1.25;
}

/* ✅ Red dot + label marker (no image/svg) */
.event-marker {
  background: transparent;
  border: 0;
}

.event-marker__wrap {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transform: translate(-7px, -7px);
  user-select: none;
  white-space: nowrap;
}

.event-marker__dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: #ef4444; /* red */
  border: 3px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 14px 30px rgba(239, 68, 68, 0.25);
}

.event-marker__label {
  font-size: 12px;
  font-weight: 800;
  color: #111827;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(17, 24, 39, 0.08);
  padding: 6px 10px;
  border-radius: 999px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12);
}
</style>
