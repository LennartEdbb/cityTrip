<template>
  <div class="top-ui">
    <div class="top-row">
      <EventAddPanel />
      <div class="title">City Trip</div>
      <button class="icon-btn" type="button" @click="$emit('toggle-view')">
        <span v-if="viewMode === 'map'" class="material-icons" style="color: #252525">density_small</span>
        <span v-else class="material-icons" style="color: #252525">map</span>
      </button>
    </div>

    <RadiusFilter @radius-change="$emit('radius-change', $event)" />
  </div>
</template>

<script setup lang="ts">
import EventAddPanel from "./EventAddPanel.vue"
import RadiusFilter from "./RadiusFilter.vue"
import { defineProps } from "vue"

defineProps<{ viewMode: 'map' | 'list' }>()
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
</style>
