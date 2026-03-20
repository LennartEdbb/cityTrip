<template>
  <div class="list-wrap">
    <div class="list-head">
      <div class="top-row">
        <div class="spacer"></div>

        <div class="title">Venues</div>

        <button
          class="icon-btn"
          type="button"
          @click="toggleView()"
          aria-label="Toggle map/list view"
        >
          <span class="material-icons" style="color: #252525">map</span>
        </button>
      </div>

      <div class="filters">
        <input class="filter-input" placeholder="Suchen..." v-model="q" />

        <div class="date-filters">
          <select class="filter-select" v-model="selectedMonth">
            <option value="">Monat wählen</option>
            <option
              v-for="month in months"
              :key="month.value"
              :value="month.value"
            >
              {{ month.label }}
            </option>
          </select>

          <select class="filter-select" v-model="selectedDay">
            <option value="">Tag wählen</option>
            <option
              v-for="day in daysInSelectedMonth"
              :key="day"
              :value="String(day)"
            >
              {{ day }}
            </option>
          </select>
        </div>

        <label class="filter-check">
          <input type="checkbox" v-model="accessibleOnly" />
          Barrierefrei
        </label>

        <div class="tag-filters" v-if="tags.length">
          <label
            v-for="t in tags"
            :key="t"
            class="filter-check tag-check"
          >
            <input
              type="checkbox"
              :value="t"
              v-model="selectedTags"
            />
            {{ t }}
          </label>
        </div>
      </div>

      <div class="list-sub">
        Showing {{ filtered.length }} of {{ venues.length }}
        <span v-if="typeof radius === 'number'"> · Radius: {{ radius }}km</span>
      </div>
    </div>

    <div v-if="!venues?.length" class="empty">
      No venues found.
    </div>

    <div v-else class="cards">
      <button
        v-for="v in filtered"
        :key="v.id"
        class="card"
        type="button"
        @click="onSelect(v)"
      >
        <div class="row">
          <div class="name">{{ v.name }}</div>
          <div class="dist" v-if="v.distanceText">{{ v.distanceText }}</div>
        </div>

        <div class="addr">{{ v.address }}</div>

        <div class="meta" v-if="v.whenText || v.priceText || v.accessible">
          <span v-if="v.whenText">{{ v.whenText }}</span>
          <span v-if="v.whenText && (v.priceText || v.accessible)"> · </span>

          <span v-if="v.priceText">{{ v.priceText }}</span>
          <span v-if="v.priceText && v.accessible"> · </span>

          <span v-if="v.accessible" class="badge">♿ Accessible</span>
        </div>

        <div class="tags" v-if="v.tags?.length">
          <span v-for="t in v.tags" :key="t" class="tag">{{ t }}</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

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


const props = defineProps<{
  venues: Venue[]
  radius?: number
}>()

const emit = defineEmits<{
  (e: "select", v: Venue): void
  (e: "toggle-view"): void
}>()

function onSelect(v: Venue) {
  emit("select", v)
}

function toggleView() {
  emit("toggle-view")
}

const q = ref("")
const accessibleOnly = ref(false)
const selectedTags = ref<string[]>([])
const selectedMonth = ref("")
const selectedDay = ref("")

const months = [
  { value: "1", label: "Januar" },
  { value: "2", label: "Februar" },
  { value: "3", label: "März" },
  { value: "4", label: "April" },
  { value: "5", label: "Mai" },
  { value: "6", label: "Juni" },
  { value: "7", label: "Juli" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "Oktober" },
  { value: "11", label: "November" },
  { value: "12", label: "Dezember" },
]

const tags = computed(() => {
  const s: string[] = []
  for (const v of props.venues || []) {
    for (const t of v.tags || []) {
      if (t && !s.includes(t)) s.push(t)
    }
  }
  return s.sort()
})

const daysInSelectedMonth = computed(() => {
  const month = Number(selectedMonth.value)

  if (!month) {
    return Array.from({ length: 31 }, (_, i) => i + 1)
  }

  const days = new Date(2024, month, 0).getDate()
  return Array.from({ length: days }, (_, i) => i + 1)
})

watch(selectedMonth, () => {
  if (!selectedDay.value) return

  const days = daysInSelectedMonth.value
  if (!days.length) return
  const maxDay = days[days.length - 1] || 0
  if (Number(selectedDay.value) > maxDay) {
    selectedDay.value = ""
  }
})

function parseVenueDate(value?: string) {
  if (!value) return null

  const parsed = new Date(value)
  if (!Number.isNaN(parsed.getTime())) {
    return {
      day: parsed.getDate(),
      month: parsed.getMonth() + 1,
    }
  }

  const ddmmyyyy = value.match(/\b(\d{1,2})[.\-/](\d{1,2})(?:[.\-/]\d{2,4})?\b/)
  if (ddmmyyyy) {
    return {
      day: Number(ddmmyyyy[1]),
      month: Number(ddmmyyyy[2]),
    }
  }

  return null
}

const filtered = computed(() => {
  let list = props.venues ?? []
  if (q.value) {
    const qq = q.value.toLowerCase()
    list = list.filter((v) =>
      (v.name + " " + v.address + " " + (v.tags || []).join(" "))
        .toLowerCase()
        .includes(qq)
    )
  }

  if (accessibleOnly.value) {
    list = list.filter((v) => !!v.accessible)
  }

  if (selectedTags.value.length) {
    list = list.filter((v) =>
      selectedTags.value.some((tag) => (v.tags || []).includes(tag))
    )
  }

  if (selectedMonth.value || selectedDay.value) {
    list = list.filter((v) => {
      const venueDate = parseVenueDate(v.whenText)
      if (!venueDate) return false

      if (selectedMonth.value && venueDate.month !== Number(selectedMonth.value)) {
        return false
      }

      if (selectedDay.value && venueDate.day !== Number(selectedDay.value)) {
        return false
      }

      return true
    })
  }

  return list
})
</script>

<style scoped>
.filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: stretch;
  justify-content: center;
  margin-bottom: 8px;
}

.filter-input,
.filter-select {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #dbe3ee;
  background: #fff;
}

.date-filters {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.filter-check {
  font-size: 13px;
  color: #334155;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.tag-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.tag-check {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid #dbe3ee;
  background: #fff;
}

.list-wrap {
  padding: 14px 14px 24px;
}

.list-head {
  padding: 10px 6px 14px;
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
  text-transform: uppercase;
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
  cursor: pointer;
  pointer-events: auto;
}

.icon-btn span,
.icon-btn svg {
  width: 20px;
  height: 20px;
  color: #111827;
}

.list-sub {
  margin-top: 8px;
  font-size: 12px;
  color: rgba(17, 24, 39, 0.6);
  text-align: center;
}

.empty {
  margin: 18px 6px;
  padding: 14px 12px;
  border-radius: 14px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.92);
  color: rgba(17, 24, 39, 0.7);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
}

.cards {
  display: grid;
  gap: 12px;
}

.card {
  width: 100%;
  text-align: left;
  border-radius: 16px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.92);
  padding: 12px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.08);
  cursor: pointer;
}

.row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}

.name {
  font-weight: 900;
  color: #111827;
  font-size: 14px;
  line-height: 1.2;
}

.dist {
  font-weight: 800;
  font-size: 12px;
  color: rgba(17, 24, 39, 0.65);
  white-space: nowrap;
}

.addr {
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.3;
  color: rgba(17, 24, 39, 0.65);
}

.meta {
  margin-top: 8px;
  font-size: 12px;
  color: rgba(17, 24, 39, 0.7);
}

.badge {
  font-weight: 800;
}

.tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 11px;
  font-weight: 800;
  color: #111827;
  background: rgba(17, 24, 39, 0.06);
  border: 1px solid rgba(17, 24, 39, 0.08);
  padding: 5px 10px;
  border-radius: 999px;
}
</style>