<template>
  <div v-if="show && venues.length" class="sheet">
    <div class="sheet-handle" />
    <div class="cards">
      <div v-for="(v, idx) in venues" :key="v.id" class="card" @click="$emit('select', v)">
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
              title="Favourite"
            >
              <span class="heart-ic" :class="{ on: isFav(v.id) }">♥</span>
            </button>

            <div class="distance">
              <span class="pin">📍</span>
              <span>{{ v.distanceText ?? "—" }}</span>
            </div>
          </div>
        </div>

        <div class="card-mid" v-if="v.whenText || v.priceText || v.accessible">
          <span v-if="v.whenText">🗓️ {{ v.whenText }}</span>
          <span v-if="v.priceText">🎟️ {{ v.priceText }}</span>
          <span v-if="v.accessible">♿ barrierefrei</span>
        </div>

        <div class="tag-row" v-if="v.tags?.length">
          <span class="tag" v-for="t in v.tags" :key="t">{{ t }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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
  margin: 0 auto 10px auto;
}

.cards {
  pointer-events: auto;
  display: flex;
  gap: 12px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scroll-snap-type: x mandatory;
  padding-bottom: 4px;


  scrollbar-width: none;
  -ms-overflow-style: none;
  overscroll-behavior-x: contain;
}

.cards::-webkit-scrollbar {
  display: none;
}

.card {
  flex: 0 0 min(340px, calc(100vw - 28px));
  scroll-snap-align: start;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.96);
  border-radius: 18px;
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

.right {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.heart {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.92);
  display: grid;
  place-items: center;
  cursor: pointer;
}

.heart-ic {
  font-size: 16px;
  line-height: 1;
  color: rgba(17, 24, 39, 0.35);
  transform: translateY(-1px);
}

.heart-ic.on {
  color: #ef4444;
}

@media (min-width: 900px) {
  .sheet {
    left: 50%;
    right: auto;
    transform: translateX(-50%);
    width: min(1108px, calc(100vw - 40px));
  }

  .cards {
    gap: 14px;
  }

  .card {
    flex: 0 0 360px;
  }
}
</style>