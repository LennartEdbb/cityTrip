<template>
    <button class="venue-toggle" type="button" @click="open = true">
        Venues <span class="venue-toggle__count">{{ filteredVenues.length }}</span>
    </button>


    <Teleport to="body">
        <Transition name="overlay-fade">
        <div
            v-if="open"
            class="overlay"
            role="dialog"
            aria-modal="true"
            @click.self="open = false"
            @keydown.esc="open = false"
            tabindex="-1"
        >
            <div class="panel">
            <div class="panel__header">
                <div class="panel__title">
                <h2>Venues</h2>
                <span class="panel__subtitle">{{ filteredVenues.length }} results</span>
                </div>

                <button class="close-btn" type="button" @click="open = false" aria-label="Close">
                ✕
                </button>
            </div>

            <div class="panel__content">
                <div v-if="filteredVenues.length === 0" class="empty">
                No venues in the selected radius.
                </div>

                <div
                v-for="venue in filteredVenues"
                :key="venue.id"
                class="venue-card"
                >
                <div class="venue-card__top">
                    <h3 class="venue-card__name">
                    {{ venue.name }}
                    <span v-if="venue.accessible" class="badge" title="Accessible">♿</span>
                    </h3>
                    <span v-if="venue.distanceText" class="meta">
                    {{ venue.distanceText }}
                    </span>
                </div>

                <p class="venue-card__address">{{ venue.address }}</p>

                <div class="venue-card__meta">
                    <span v-if="venue.whenText" class="pill">🗓️ {{ venue.whenText }}</span>
                    <span v-if="venue.priceText" class="pill">💶 {{ venue.priceText }}</span>
                </div>

                <div v-if="venue.tags?.length" class="tags">
                    <span v-for="tag in venue.tags" :key="tag" class="tag">{{ tag }}</span>
                </div>
                </div>
            </div>
            <div class="panel__footer">
                <button class="secondary" type="button" @click="open = false">Close</button>
            </div>
            </div>
        </div>
        </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'

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

const open = ref(false)

const filteredVenues = computed(() => {
  if (!props.radius) return props.venues
  return props.venues.filter(v => v.distanceM != null && v.distanceM <= (props.radius || 10) * 1000)
})

watch(open, (v) => {
  if (typeof document === 'undefined') return
  document.body.style.overflow = v ? 'hidden' : ''
})

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') open.value = false
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.venue-toggle {
  position: fixed;
  right: 16px;
  bottom: 16px;
  z-index: 30;
  border: 0;
  border-radius: 999px;
  padding: 10px 14px;
  font-weight: 600;
  background: #111827;
  color: #fff;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  cursor: pointer;
  display: inline-flex;
  gap: 10px;
  align-items: center;
}
.venue-toggle:hover { transform: translateY(-1px); }
.venue-toggle:active { transform: translateY(0px); }
.venue-toggle__count{
  background: rgba(255,255,255,0.15);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
}

.overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(6px);
  display: grid;
  place-items: center;
  padding: 16px;
}

.panel {
  width: min(720px, 100%);
  max-height: min(82vh, 900px);
  background: rgba(255,255,255,0.9);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.25);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel__header {
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0,0,0,0.06);
}
.panel__title h2 {
  margin: 0;
  font-size: 16px;
  letter-spacing: -0.01em;
}
.panel__subtitle {
  display: inline-block;
  margin-top: 2px;
  font-size: 12px;
  color: rgba(0,0,0,0.6);
}

.close-btn {
  border: 0;
  background: rgba(0,0,0,0.06);
  width: 34px;
  height: 34px;
  border-radius: 10px;
  cursor: pointer;
}
.close-btn:hover { background: rgba(0,0,0,0.1); }

.panel__content {
  padding: 14px 16px;
  overflow: auto;
}

.empty {
  padding: 18px;
  border-radius: 12px;
  background: rgba(0,0,0,0.04);
  color: rgba(0,0,0,0.65);
  font-size: 14px;
}

.venue-card {
  background: rgba(255,255,255,0.95);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 12px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.08);
  transition: transform 140ms ease, box-shadow 140ms ease;
}
.venue-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(0,0,0,0.12);
}

.venue-card__top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
}
.venue-card__name {
  margin: 0;
  font-size: 16px;
  letter-spacing: -0.01em;
  line-height: 1.2;
}
.badge {
  margin-left: 8px;
  font-size: 13px;
  vertical-align: middle;
  background: rgba(16,185,129,0.12);
  color: #065f46;
  border: 1px solid rgba(16,185,129,0.25);
  padding: 2px 6px;
  border-radius: 999px;
}

.meta {
  font-size: 12px;
  color: rgba(0,0,0,0.55);
  white-space: nowrap;
}

.venue-card__address {
  margin: 6px 0 0 0;
  color: rgba(0,0,0,0.72);
  font-size: 13px;
}

.venue-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.pill {
  font-size: 12px;
  color: rgba(0,0,0,0.7);
  background: rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.06);
  padding: 6px 10px;
  border-radius: 999px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.tag {
  background: rgba(59,130,246,0.10);
  border: 1px solid rgba(59,130,246,0.20);
  color: #1d4ed8;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.panel__footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(0,0,0,0.06);
  display: flex;
  justify-content: flex-end;
}
.secondary {
  border: 1px solid rgba(0,0,0,0.12);
  background: rgba(255,255,255,0.8);
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
}
.secondary:hover { background: rgba(0,0,0,0.03); }

.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 140ms ease;
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}
</style>