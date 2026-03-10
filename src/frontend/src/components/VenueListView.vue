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

      <div class="list-sub">
        Showing {{ venues.length }} {{ venues.length === 1 ? "place" : "places" }}
        <span v-if="typeof radius === 'number'"> · Radius: {{ radius }}km</span>
      </div>
    </div>

    <div v-if="!venues?.length" class="empty">
      No venues found.
    </div>

    <div v-else class="cards">
      <button
        v-for="v in venues"
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

defineProps<{
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
</script>

<style scoped>
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