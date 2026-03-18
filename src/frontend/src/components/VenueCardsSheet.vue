<template>
  <div v-if="show && venues.length" ref="sheetRef" class="sheet">
    <div class="sheet-handle" />

    <div class="cards">
      <div
        v-for="(v, idx) in venues"
        :key="v.id"
        class="card"
        :class="{
          expanded: expandedId === v.id,
          lowered: expandedId !== null && expandedId !== v.id
        }"
        role="button"
        tabindex="0"
        @click="toggleExpand(v)"
        @keydown.enter.prevent="toggleExpand(v)"
        @keydown.space.prevent="toggleExpand(v)"
      >
        <div class="card-top">
          <div class="card-title">
            <span class="rank">{{ idx + 1 }}.</span>
            <span class="name">{{ v.name }}</span>
          </div>

          <div class="right">
            <button
              class="heart"
              type="button"
              :aria-pressed="isFav(v.id)"
              @click.stop="$emit('toggle-fav', v.id)"
            >
              <span class="heart-ic" :class="{ on: isFav(v.id) }">♥</span>
            </button>

            <div class="distance">
              <span class="material-icons">location_pin</span>
              {{ formatDistance(v) }}
            </div>
          </div>
        </div>

        <div v-if="v.creatorName" class="creator-row">
          <span class="material-icons">person</span>
          <span>{{ v.creatorName }}</span>
        </div>

        <div class="compact-row" v-if="expandedId !== v.id">
          <span v-if="v.whenText" class="mini-chip time-chip">
            <span class="material-icons">calendar_month</span>
            <span class="time-text">{{ v.whenText }}</span>
          </span>

          <span v-if="v.priceText" class="mini-chip">
            <span class="material-icons">payments</span>
            {{ v.priceText }}
          </span>
        </div>

        <transition name="expand">
          <div v-if="expandedId === v.id" class="expanded-content">
            <div
              class="card-mid"
              v-if="v.whenText || v.priceText || v.accessible !== undefined"
            >
              <span v-if="v.whenText">
                <span class="material-icons">calendar_month</span>
                {{ v.whenText }}
              </span>

              <span v-if="v.priceText">
                <span class="material-icons">payments</span>
                {{ v.priceText }}
              </span>

              <span v-if="v.accessible === true">
                <span class="material-icons">accessible</span>
                Accessible
              </span>

              <span v-if="v.accessible === false">
                <span class="material-icons">not_accessible</span>
                Not accessible
              </span>
            </div>

            <div v-if="v.creatorName" class="address creator-detail">
              <span class="material-icons">person</span>
              Erstellt von: {{ v.creatorName }}
            </div>

            <div class="address" v-if="v.address">
              <span class="material-icons">place</span>
              {{ v.address }}
            </div>

            <div class="meta" v-if="v.distanceM != null">
              {{ formatDistance(v) }} away
            </div>

            <div class="tag-row" v-if="v.tags?.length">
              <span class="tag" v-for="t in v.tags" :key="t">{{ t }}</span>
            </div>

            <button
              class="open-btn"
              type="button"
              @click.stop="$emit('select', v)"
            >
              Show Route
            </button>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue"

type Venue = {
  id: string
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
  creatorName?: string
}

defineProps<{
  venues: Venue[]
  show: boolean
  isFav: (id: string) => boolean
}>()

defineEmits<{
  (e: "select", v: Venue): void
  (e: "toggle-fav", id: string): void
}>()

const expandedId = ref<string | null>(null)
const sheetRef = ref<HTMLElement | null>(null)

function toggleExpand(v: Venue) {
  expandedId.value = expandedId.value === v.id ? null : v.id
}

function formatDistance(v: Venue) {
  if (v.distanceM == null) return v.distanceText ?? "—"

  if (v.distanceM < 1000) {
    return `${Math.round(v.distanceM)} m`
  }

  return `${(v.distanceM / 1000).toFixed(1)} km`
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as Node | null
  if (!sheetRef.value || !target) return

  if (!sheetRef.value.contains(target)) {
    expandedId.value = null
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside)
})
</script>

<style scoped>
.sheet {
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: calc(var(--nav-bottom) + var(--nav-h) + var(--nav-gap));
  z-index: 600;
  pointer-events: none;
}

.sheet-handle {
  width: 52px;
  height: 5px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.14);
  margin: 0 auto 10px;
}

.cards {
  pointer-events: auto;
  display: flex;
  gap: 12px;
  overflow-x: auto;
  overflow-y: visible;
  scroll-snap-type: x mandatory;
  scroll-padding-left: 14px;
  padding: 0 14px 18px;
  box-sizing: border-box;
  justify-content: flex-start;
  align-items: flex-start;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.cards::-webkit-scrollbar {
  display: none;
}

.card {
  position: relative;
  flex: 0 0 calc(100% - 28px);
  max-width: 420px;
  min-width: 280px;
  scroll-snap-align: start;
  box-sizing: border-box;
  border-radius: 16px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: white;
  padding: 14px;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease,
    opacity 0.25s ease;
  transform: translateY(0) scale(1);
  transform-origin: center center;
  z-index: 1;
}

.card.expanded {
  transform: translateY(0) scale(1.04);
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.12);
  z-index: 3;
}

.card.lowered {
  transform: translateY(140px) scale(0.98);
  z-index: 1;
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.card-title {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-weight: 700;
  min-width: 0;
  flex: 1;
  pointer-events: none;
}

.time-text {
  max-width: 70ch;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.rank {
  color: #64748b;
  font-size: 13px;
  flex-shrink: 0;
  margin-top: 1px;
}

.name {
  font-size: 15px;
  line-height: 1.3;
  color: #111827;
  min-width: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.distance {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
  pointer-events: none;
}

.material-icons {
  font-size: 16px;
  flex-shrink: 0;
}

.heart {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  border: 1px solid rgba(17, 24, 39, 0.1);
  background: white;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.heart-ic {
  color: rgba(17, 24, 39, 0.4);
}

.heart-ic.on {
  color: #ef4444;
}

.compact-row {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mini-chip {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.05);
  display: inline-flex;
  gap: 4px;
  align-items: center;
  min-width: 0;
}

.expanded-content {
  margin-top: 10px;
}

.card-mid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
}

.card-mid span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(17, 24, 39, 0.05);
  padding: 4px 8px;
  border-radius: 999px;
}

.address {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.4;
  color: #475569;
  display: flex;
  align-items: flex-start;
  gap: 4px;
}

.meta {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}

.tag-row {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-size: 11px;
  padding: 4px 8px;
  background: rgba(17, 24, 39, 0.06);
  border-radius: 999px;
}

.open-btn {
  margin-top: 10px;
  width: 100%;
  border: none;
  background: #2563eb;
  color: white;
  padding: 9px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.creator-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
}

.creator-row .material-icons,
.creator-detail .material-icons {
  font-size: 16px;
}

.creator-detail {
  margin-top: 8px;
}

@media (max-width: 480px) {
  .sheet {
    left: 10px;
    right: 10px;
  }

  .cards {
    padding: 0 10px 18px;
    scroll-padding-left: 10px;
  }

  .card {
    flex-basis: calc(100% - 20px);
    padding: 12px;
  }

  .distance {
    font-size: 11px;
  }

  .name {
    font-size: 14px;
  }
 
  .card.lowered {
  transform: translateY(157px) scale(0.98);
  z-index: 1;
}
}

@media (min-width: 900px) {
  .sheet {
    left: 50%;
    transform: translateX(-50%);
    width: min(1100px, calc(100vw - 40px));
  }

  .cards {
    justify-content: flex-start;
    padding: 0 14px 18px;
    scroll-padding-left: 14px;
  }

  .card {
    flex: 0 0 360px;
    max-width: 360px;
  }
}
</style>