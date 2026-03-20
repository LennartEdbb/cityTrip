<template>
  <div class="fav-view">
    <header class="fav-head">
      <div>
        <p class="fav-eyebrow">Saved places</p>
        <h1 class="fav-title">Your favourites</h1>
        <p class="fav-sub">
          {{ favourites.length }}
          {{ favourites.length === 1 ? "venue" : "venues" }} saved
        </p>
      </div>

      <div class="fav-head-icon">
        <span class="material-icons" style="color: red;">
        favorite
        </span>
      </div>
    </header>

    <div v-if="!favourites.length" class="empty">
      <div class="empty-ic">
        <span class="material-icons" style="color: red;">
          favorite
        </span>
      </div>
      <div class="empty-title">No favourites yet</div>
      <div class="empty-sub">Tap the heart on a venue to save it here.</div>
    </div>

    <div v-else class="fav-list">
      <button
        v-for="v in favourites"
        :key="v.id"
        class="fav-item"
        type="button"
        @click="$emit('select', v)"
      >
        <div class="row">
          <div class="left">
            <div class="name">{{ v.name }}</div>
            <div class="addr">{{ v.address }}</div>
          </div>

          <div class="right">
            <div class="dist">{{ v.distanceText ?? "—" }}</div>

            <button
              class="heart"
              type="button"
              @click.stop="toggleFavourite(v.id)"
              title="Remove from favourites"
              aria-label="Remove from favourites"
            >
              <span class="heart-ic on">♥</span>
            </button>
          </div>
        </div>

        <div class="meta" v-if="v.whenText || v.priceText || v.accessible">
          <span v-if="v.whenText">🗓️ {{ v.whenText }}</span>
          <span v-if="v.priceText">🎟️ {{ v.priceText }}</span>
          <span v-if="v.accessible">♿ Barrierefrei</span>
        </div>

        <div class="tags" v-if="v.tags?.length">
          <span class="tag" v-for="t in v.tags" :key="t">{{ t }}</span>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
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

const props = defineProps<{
  venues: Venue[]
}>()

defineEmits<{
  (e: "select", v: Venue): void
}>()

const { isFavourite, toggleFavourite } = useFavourites()

const favourites = computed(() => props.venues.filter((v) => isFavourite(v.id)))
</script>

<style scoped>
.fav-view {
  padding: 18px 16px 120px;
  min-height: 100%;
  background:
    radial-gradient(
      circle at top right,
      rgba(239, 68, 68, 0.18) 0%,
      rgba(239, 68, 68, 0.10) 18%,
      rgba(239, 68, 68, 0.04) 32%,
      transparent 55%
    ),
    #ffffff;
}

.fav-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  padding: 4px 2px 8px;
}

.fav-eyebrow {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(17, 24, 39, 0.5);
}

.fav-title {
  margin: 0;
  font-size: 24px;
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.03em;
  color: #111827;
}

.fav-sub {
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(17, 24, 39, 0.62);
  font-weight: 700;
}

.fav-head-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 22px;

  background: linear-gradient(180deg, #ffe6e6 0%, #ffcaca 100%);
  border: 1px solid rgba(239, 68, 68, 0.15);

  box-shadow: 0 10px 24px rgba(239, 68, 68, 0.15);
}

.empty {
  margin-top: 44px;
  text-align: center;
  padding: 28px 20px;
  border: 1px dashed rgba(17, 24, 39, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
}

.empty-ic {
  font-size: 40px;
}

.empty-title {
  margin-top: 12px;
  font-weight: 900;
  font-size: 18px;
  color: #111827;
}

.empty-sub {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.45;
  color: rgba(17, 24, 39, 0.62);
  font-weight: 700;
}

.fav-list {
  display: grid;
  gap: 12px;
}

.fav-item {
  width: 100%;
  text-align: left;
  border: 1px solid rgba(17, 24, 39, 0.07);
  background: rgba(255, 255, 255, 0.94);
  border-radius: 20px;
  padding: 14px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(17, 24, 39, 0.06);
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease;
}

.fav-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(17, 24, 39, 0.1);
  border-color: rgba(17, 24, 39, 0.12);
}

.fav-item:active {
  transform: translateY(0);
}

.row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.left {
  min-width: 0;
  flex: 1;
}

.name {
  font-weight: 900;
  font-size: 15px;
  color: #111827;
  line-height: 1.25;
  letter-spacing: -0.01em;
}

.addr {
  margin-top: 5px;
  font-size: 13px;
  color: rgba(17, 24, 39, 0.58);
  font-weight: 700;
  line-height: 1.4;
}

.right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.dist {
  font-size: 12px;
  color: rgba(17, 24, 39, 0.5);
  font-weight: 800;
  white-space: nowrap;
  padding: 6px 8px;
  border-radius: 999px;
  background: rgba(17, 24, 39, 0.05);
}

.heart {
  width: 36px;
  height: 36px;
  border-radius: 999px;
  border: 1px solid rgba(239, 68, 68, 0.14);
  background: #fff5f5;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition:
    transform 0.16s ease,
    background 0.16s ease;
}

.heart:hover {
  transform: scale(1.05);
  background: #ffecec;
}

.heart-ic {
  font-size: 16px;
  line-height: 1;
  transform: translateY(-1px);
  color: rgba(17, 24, 39, 0.35);
}

.heart-ic.on {
  color: #ef4444;
}

.meta {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta span {
  font-size: 12px;
  color: rgba(17, 24, 39, 0.78);
  font-weight: 700;
  background: rgba(17, 24, 39, 0.045);
  border-radius: 999px;
  padding: 6px 10px;
}

.tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 12px;
  color: rgba(17, 24, 39, 0.68);
  background: rgba(17, 24, 39, 0.055);
  border: 1px solid rgba(17, 24, 39, 0.05);
  border-radius: 999px;
  padding: 6px 10px;
  font-weight: 700;
}
</style>