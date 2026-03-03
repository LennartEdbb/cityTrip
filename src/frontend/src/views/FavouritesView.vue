<template>
  <div class="fav-view">
    <div class="fav-head">
      <div class="fav-title">Favourites</div>
      <div class="fav-sub">{{ favourites.length }} saved</div>
    </div>

    <div v-if="!favourites.length" class="empty">
      <div class="empty-ic">💛</div>
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

            <button class="heart" type="button" @click.stop="toggleFavourite(v.id)" title="Remove">
              <span class="heart-ic on">♥</span>
            </button>
          </div>
        </div>

        <div class="meta" v-if="v.whenText || v.priceText || v.accessible">
          <span v-if="v.whenText">🗓️ {{ v.whenText }}</span>
          <span v-if="v.priceText">🎟️ {{ v.priceText }}</span>
          <span v-if="v.accessible">♿ barrierefrei</span>
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
  padding: 14px 14px 120px 14px;
}

.fav-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.fav-title {
  font-weight: 900;
  letter-spacing: 0.04em;
  font-size: 14px;
  color: #111827;
}

.fav-sub {
  font-size: 12px;
  color: rgba(17, 24, 39, 0.6);
  font-weight: 700;
}

.empty {
  margin-top: 60px;
  text-align: center;
  padding: 20px;
}

.empty-ic {
  font-size: 34px;
}

.empty-title {
  margin-top: 10px;
  font-weight: 900;
  color: #111827;
}

.empty-sub {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(17, 24, 39, 0.6);
  font-weight: 700;
}

.fav-list {
  display: grid;
  gap: 10px;
}

.fav-item {
  width: 100%;
  text-align: left;
  border: 1px solid rgba(17, 24, 39, 0.08);
  background: rgba(255, 255, 255, 0.96);
  border-radius: 18px;
  padding: 12px 12px 10px 12px;
  cursor: pointer;
}

.row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.left {
  min-width: 0;
}

.name {
  font-weight: 900;
  font-size: 13px;
  color: #111827;
  line-height: 1.2;
}

.addr {
  margin-top: 3px;
  font-size: 12px;
  color: rgba(17, 24, 39, 0.6);
  font-weight: 700;
  line-height: 1.25;
}

.right {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.dist {
  font-size: 12px;
  color: rgba(17, 24, 39, 0.55);
  font-weight: 800;
  white-space: nowrap;
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
  transform: translateY(-1px);
  color: rgba(17, 24, 39, 0.35);
}

.heart-ic.on {
  color: #ef4444;
}

.meta {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: rgba(17, 24, 39, 0.8);
  font-weight: 700;
}

.tags {
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
</style>