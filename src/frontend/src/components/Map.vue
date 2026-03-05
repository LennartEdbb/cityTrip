<template>
  <div class="map-shell">
    <!-- Top header -->
    <div class="top-ui">
      <div class="top-row">
        <EventAddPanel />
        <div class="title">City Trip</div>
        <button class="icon-btn" type="button" @click="toggleViewMode">
          <svg
            v-if="viewMode === 'map'"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
          <svg
            v-else
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M3 7V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7M3 7l9 4 9-4"
            />
          </svg>
        </button>
      </div>
      <RadiusFilter @radius-change="onRadiusChange" />
    </div>

    <div ref="mapEl" class="map" v-show="viewMode === 'map'" />

    <div class="list-layer" v-show="viewMode === 'list'">
      <FavouritesView
        v-if="activeTab === 'favourites'"
        :venues="sortedVenues"
        @select="focusVenue"
      />
      <VenueListView
        v-else
        :venues="filteredVenues"
        :radius="radius"
        @select="focusVenue"
      />
    </div>

    <VenueCardsSheet
      :show="viewMode === 'map'"
      :venues="filteredVenues"
      :isFav="isFavourite"
      @toggle-fav="toggleFavourite"
      @select="focusVenue"
    />

    <!-- bottom nav -->
    <BottomNav
      :activeTab="activeTab"
      @tab="onTab"
    />

    <OwnLocation @location-obtained="addUserMarker" />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import OwnLocation from "./OwnLocation.vue"
import EventAddPanel from "./EventAddPanel.vue"
import RadiusFilter from "./RadiusFilter.vue"
import VenueListView from "./VenueListView.vue"
import BottomNav from "./BottomNav.vue"
import VenueCardsSheet from "./VenueCardsSheet.vue"
import FavouritesView from "@/views/FavouritesView.vue"
import { useFavourites } from "@/store/favourites"

type Venue = {
  id: string
  label?: string

  name: string
  address: string
  tags?: string[]

  whenText?: string
  priceText?: string
  accessible?: boolean

  lat?: number
  lng?: number
  distanceM?: number
  distanceText?: string
}

type ZeitmodellEinmalig = {
  typ: "einmalig"
  id?: number
  datum: string // YYYY-MM-DD
  von?: string | null // HH:mm:ss
  bis?: string | null
  hinweis?: string | null
}

type ZeitmodellSerie = {
  typ: "serie"
  id?: number
  gueltig_von: string // YYYY-MM-DD
  gueltig_bis: string // YYYY-MM-DD
  von?: string | null
  bis?: string | null
  intervall_wochen?: number | null
  wochentage?: string[] | null // ["Montag", ...]
  hinweis?: string | null
}

type ZeitmodellSlot = {
  id?: number
  wochentag: string // "Montag" ...
  uhrzeit_von: string // HH:mm:ss
  uhrzeit_bis: string // HH:mm:ss
}

type ZeitmodellDurchgaengig = {
  typ: "durchgaengig"
  id?: number
  gueltig_von?: string | null
  gueltig_bis?: string | null
  slots?: ZeitmodellSlot[] | null
  hinweis?: string | null
}

type ApiZeitmodell = ZeitmodellEinmalig | ZeitmodellSerie | ZeitmodellDurchgaengig

type ApiEvent = {
  id: number
  bezeichnung: string
  beschreibung?: string | null
  bemerkung?: string | null
  barrierefrei: boolean
  aktiv: boolean
  kategorien: string[]
  location: {
    id: number
    bezeichnung: string
    beschreibung?: string | null
    bemerkung?: string | null
    lat: number
    lon: number
    anschrift: {
      strasse: string
      hausnummer: string
      ort: string
      plz: string
      land: string
      id?: number
    }
  }
  zeitmodell: ApiZeitmodell
  eintritt: {
    id?: number
    kostenmodell: string // Kostenlos | Gebühr | ...
    hinweis?: string | null
    tarife?: Array<{
      bezeichnung: string
      dauer_typ?: string
      dauer_wert?: number
      preis: number
      kriterium?: string
      waehrung: string
      id?: number
    }>
  }
}

const mapEl = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null

let routeLine: L.Polyline | null = null
let userLatLng: L.LatLng | null = null
let userMarker: L.CircleMarker | null = null
let accuracyHalo: L.Circle | null = null
let radiusCircle: L.Circle | null = null

let venueMarkers = new Map<string, L.Marker>()

const venues = ref<Venue[]>([])
const viewMode = ref<"map" | "list">("map")
const radius = ref(10) // km

const activeTab = ref<"home" | "favourites" | "settings">("home")

const { isFavourite, toggleFavourite } = useFavourites()

const sortedVenues = computed(() => {
  const list = [...venues.value]
  const hasDistances = list.some((v) => typeof v.distanceM === "number")
  if (!hasDistances) return list
  return list.sort((a, b) => (a.distanceM ?? 9e15) - (b.distanceM ?? 9e15))
})

const filteredVenues = computed(() => {
  return sortedVenues.value.filter((v) => !v.distanceM || v.distanceM <= radius.value * 1000)
})

const favouriteVenues = computed(() => {
  return sortedVenues.value.filter((v) => isFavourite(v.id))
})

const listVenues = computed(() => {
  return activeTab.value === "favourites" ? favouriteVenues.value : filteredVenues.value
})

function onTab(t: "home" | "favourites" | "settings") {
  activeTab.value = t

  if (t === "favourites") {
    viewMode.value = "list"
  } else if (t === "home") {
    viewMode.value = "map"
  } else {
  }
}

function toggleViewMode() {
  viewMode.value = viewMode.value === "map" ? "list" : "map"
}

watch(viewMode, async (mode) => {
  if (mode === "map") {
    await nextTick()
    map?.invalidateSize()
    updateMarkers()
  }
})

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
    iconSize: [1, 1],
    iconAnchor: [7, 7],
    popupAnchor: [0, -12],
  })
}

function createPopupContent(v: Venue) {
  const extra = [v.whenText, v.priceText].filter(Boolean).join(" · ")
  return `
    <div class="popup">
      <div class="popup-title">${escapeHtml(v.name)}</div>
      <div class="popup-sub">${escapeHtml(v.address)}</div>
      ${extra ? `<div class="popup-sub">${escapeHtml(extra)}</div>` : ""}
    </div>
  `
}

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

  if (viewMode.value !== "map") viewMode.value = "map"

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

function centerOnUser(zoom = 16) {
  if (!map || !userLatLng) return
  map.setView(userLatLng, zoom, { animate: false })
}

function onRadiusChange(newRadius: number) {
  radius.value = newRadius
  if (radiusCircle && userLatLng) radiusCircle.setRadius(newRadius * 1000)
  updateMarkers()
}

function updateMarkers() {
  if (!map) return
  if (viewMode.value !== "map") return

  clearVenueMarkers()
  const bounds = L.latLngBounds([])

  for (const v of filteredVenues.value) {
    if (typeof v.lat !== "number" || typeof v.lng !== "number") continue
    const coords = L.latLng(v.lat, v.lng)
    const marker = L.marker(coords, { icon: createRedDotLabelIcon(v.label) })
    marker.bindPopup(createPopupContent(v), { className: "clean-popup", closeButton: false })
    marker.addTo(map)
    venueMarkers.set(v.id, marker)
    bounds.extend(coords)
  }
  if (!userLatLng && bounds.isValid()) {
    map.fitBounds(bounds, { padding: [60, 180], maxZoom: 16 })
  }
}

function hhmm(t?: string | null) {
  return t ? t.slice(0, 5) : ""
}

function fmtTimeRange(von?: string | null, bis?: string | null) {
  const a = hhmm(von)
  const b = hhmm(bis)
  if (a && b) return `${a}–${b}`
  if (a) return a
  return ""
}

function uniq<T>(arr: T[]) {
  return Array.from(new Set(arr))
}

function fmtWhen(z: ApiZeitmodell) {
  if (!z) return undefined

  if (z.typ === "einmalig") {
    const time = fmtTimeRange(z.von, z.bis)
    return `${z.datum}${time ? ` · ${time}` : ""}`
  }

  if (z.typ === "serie") {
    const days = (z.wochentage ?? []).filter(Boolean).join(", ")
    const time = fmtTimeRange(z.von, z.bis)
    const every =
      z.intervall_wochen && z.intervall_wochen > 1 ? `alle ${z.intervall_wochen} Wochen` : "wöchentlich"

    const range = `${z.gueltig_von}–${z.gueltig_bis}`
    const parts = [range, days || undefined, time || undefined, every].filter(Boolean)

    return parts.join(" · ")
  }

  // durchgaengig
  const slots = (z.slots ?? []).filter(Boolean)
  if (!slots.length) return "Öffnungszeiten"

  const dayMap: Record<string, string> = {
    Montag: "Mo",
    Dienstag: "Di",
    Mittwoch: "Mi",
    Donnerstag: "Do",
    Freitag: "Fr",
    Samstag: "Sa",
    Sonntag: "So",
  }

  const lines = slots.map((s) => {
    const d = dayMap[s.wochentag] ?? s.wochentag
    const tr = fmtTimeRange(s.uhrzeit_von, s.uhrzeit_bis)
    return `${d} ${tr}`.trim()
  })

  const short = uniq(lines).slice(0, 3).join(" · ")
  return lines.length > 3 ? `${short} · …` : short
}

function fmtPrice(e: ApiEvent) {
  if (!e.eintritt) return undefined
  if (e.eintritt.kostenmodell?.toLowerCase() === "kostenlos") return "Kostenlos"
  const t = e.eintritt.tarife?.[0]
  if (t && Number.isFinite(t.preis)) return `${t.preis} ${t.waehrung}`
  return e.eintritt.kostenmodell
}

function toVenue(e: ApiEvent): Venue {
  const a = e.location?.anschrift
  const address = a
    ? `${a.strasse} ${a.hausnummer}, ${a.plz} ${a.ort}, ${a.land}`
    : e.location?.bezeichnung ?? ""

  return {
    id: String(e.id),
    name: e.bezeichnung,
    address,
    tags: e.kategorien ?? [],
    accessible: !!e.barrierefrei,
    whenText: e.zeitmodell ? fmtWhen(e.zeitmodell) : undefined,
    priceText: fmtPrice(e),
    lat: e.location?.lat,
    lng: e.location?.lon,
    label: e.bezeichnung,
  }
}

async function loadVenuesAndMarkers() {
  if (!map) return

  const API_BASE =
    (import.meta as any).env?.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000"
  const url = `${API_BASE}/activities`

  let list: ApiEvent[]
  try {
    const res = await fetch(url, {
      method: "GET",
      mode: "cors",
      cache: "no-store",
      headers: { Accept: "application/json" },
    })

    if (!res.ok) {
      const text = await res.text().catch(() => "")
      throw new Error(`GET ${url} failed: ${res.status} ${res.statusText} ${text}`)
    }

    const data = await res.json()

    list = Array.isArray(data) ? (data as ApiEvent[]) : (data?.activities as ApiEvent[])

    if (!Array.isArray(list)) {
      console.error("Server did not return ApiEvent[]:", data)
      return
    }
  } catch (err) {
    console.error("Failed to fetch events from server:", err)
    return
  }

  venues.value = list
    .filter((e) => e?.aktiv !== false)
    .map(toVenue)
    .filter((v) => Number.isFinite(v.lat) && Number.isFinite(v.lng))

  updateDistances()
  updateMarkers()
}

function addUserMarker(position: GeolocationPosition) {
  if (!map) return

  userLatLng = L.latLng(position.coords.latitude, position.coords.longitude)

  if (userMarker) map.removeLayer(userMarker)
  if (accuracyHalo) map.removeLayer(accuracyHalo)
  if (radiusCircle) map.removeLayer(radiusCircle)

  accuracyHalo = L.circle(userLatLng, {
    radius: 70,
    color: "#2f5bff",
    weight: 0,
    fillColor: "#2f5bff",
    fillOpacity: 0.12,
  }).addTo(map)

  radiusCircle = L.circle(userLatLng, {
    radius: radius.value * 1000,
    color: "#007bff",
    weight: 2,
    fillColor: "#007bff",
    fillOpacity: 0.1,
  }).addTo(map)

  updateDistances()

  userMarker = L.circleMarker(userLatLng, {
    radius: 8,
    color: "#ffffff",
    weight: 3,
    fillColor: "#2f5bff",
    fillOpacity: 1,
  }).addTo(map)

  centerOnUser(16)
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
  --nav-h: 72px;
  --nav-gap: 14px;
  --nav-bottom: calc(14px + env(safe-area-inset-bottom));
}

.map {
  position: absolute;
  inset: 0;
}

.list-layer {
  position: absolute;
  inset: 0;
  z-index: 400;
  overflow: auto;
  -webkit-overflow-scrolling: touch;

  padding-top: calc(110px + env(safe-area-inset-top));
  padding-bottom: calc(110px + env(safe-area-inset-bottom));
}

.top-ui {
  position: absolute;
  left: 18px;
  right: 18px;
  top: calc(18px + env(safe-area-inset-top));
  z-index: 500;
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

:deep(.leaflet-control-container .leaflet-bottom.leaflet-right) {
  margin-bottom: calc(var(--nav-bottom) + var(--nav-h) + 18px);
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

.event-marker {
  background: transparent;
  border: none;
}

.event-marker__circle {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 6px 14px rgba(0,0,0,0.25);
  margin: 6px;
}

.greeting-row { margin-top: 8px; display:flex; justify-content:center }
.greeting { background: rgba(255,255,255,0.9); padding:6px 12px; border-radius:999px; font-weight:700; box-shadow:0 10px 30px rgba(0,0,0,0.08) }

.logout-wrap { position: absolute; left: 50%; transform: translateX(-50%); bottom: calc(var(--nav-bottom) + var(--nav-h) + 8px); z-index: 600 }
.logout-btn { background: #fff; border: 1px solid rgba(17,24,39,0.08); padding:10px 16px; border-radius:999px; font-weight:700; box-shadow:0 12px 30px rgba(0,0,0,0.08) }

@media (min-width: 900px) {
  .map-shell {
    --nav-h: 68px;
    --nav-gap: 18px;
    --nav-bottom: 20px;
  }
}
</style>
