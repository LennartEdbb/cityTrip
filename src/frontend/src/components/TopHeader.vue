<template>
  <div class="top-ui">
    <div class="top-row">
      <div class="left-slot">
        <!-- <EventAddPanel
          v-if="canAdd"
          :events="venues"
          :currentUser="currentUser"
        /> -->
        <!-- <div v-else class="spacer"></div> -->
      </div>

      <div class="title">City Trip</div>

      <div class="right-slot">
        <button class="icon-btn" type="button" @click="$emit('toggle-view')" title="Karte/Listansicht">
          <span v-if="viewMode === 'map'" class="material-icons" style="color: #252525">density_small</span>
          <span v-else class="material-icons" style="color: #252525">map</span>
        </button>
      </div>
    </div>

    <RadiusFilter @radius-change="$emit('radius-change', $event)" />
  </div>
</template>

<script setup lang="ts">
import EventAddPanel from "./EventAddPanel.vue"
import RadiusFilter from "./RadiusFilter.vue"

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
  creatorId?: number | string
}

type CurrentUser = {
  id: number | string
  email?: string
  name?: string
  rolle?: string
}

defineProps<{
  viewMode: "map" | "list"
  canAdd?: boolean
  showRoute?: boolean
  venues?: Venue[]
  currentUser?: CurrentUser | null
}>()

defineEmits<{
  (e: "toggle-view"): void
  (e: "radius-change", value: number): void
}>()
</script>

<style scoped>
.top-ui {
  position: absolute;
  left: 18px;
  right: 18px;
  top: calc(18px + env(safe-area-inset-top));
  z-index: 500;
}

.top-row {
  display: grid;
  grid-template-columns: 88px 1fr 88px;
  align-items: center;
  gap: 10px;
}

.left-slot, .right-slot { display: flex; align-items: center; justify-content: center; gap: 8px }

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
</style>
