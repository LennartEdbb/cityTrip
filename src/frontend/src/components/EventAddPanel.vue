<template>
  <button
    class="icon-btn"
    aria-label="My events"
    @click="openPanel"
  >
    <span class="material-icons">
      bookmark
    </span>
  </button>

  <teleport to="body">
    <div v-if="isPanelOpen" class="panel-overlay" @click="closePanel">
      <div class="panel" @click.stop>
        <div class="panel-header">
          <h2 class="panel-title">My events</h2>
          <button class="header-close-btn" aria-label="Close panel" @click="closePanel">
            ×
          </button>
        </div>

        <div class="panel-content">
          <div v-if="!currentUser" class="empty-state">
            You are not logged in.
          </div>

          <div v-else-if="ownEvents.length === 0" class="empty-state">
            No own events found.
          </div>

          <div v-else class="event-list">
            <article
              v-for="event in ownEvents"
              :key="event.id"
              class="event-card"
            >
              <div class="event-card-top">
                <h3 class="event-title">{{ event.name }}</h3>
                <span v-if="event.accessible" class="badge">Accessible</span>
              </div>

              <p class="event-address">{{ event.address }}</p>

              <p v-if="event.whenText" class="event-meta">
                <strong>When:</strong> {{ event.whenText }}
              </p>

              <p v-if="event.priceText" class="event-meta">
                <strong>Price:</strong> {{ event.priceText }}
              </p>

              <div v-if="event.tags?.length" class="tag-list">
                <span
                  v-for="tag in event.tags"
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </article>
          </div>
        </div>

        <div class="panel-footer">
          <button class="close-btn" @click="closePanel">Close</button>
        </div>
      </div>
    </div>
  </teleport>
</template>
<script setup lang="ts">
import { computed, ref } from "vue"

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

const props = defineProps<{
  events?: Venue[]
  currentUser?: CurrentUser | null
}>()

const isPanelOpen = ref(false)

const ownEvents = computed(() => {
  const userId = props.currentUser?.id
  if (userId === undefined || userId === null) return []

  return (props.events ?? []).filter((event) => {
    return String(event.creatorId) === String(userId)
  })
})

function openPanel() {
  isPanelOpen.value = true
}

function closePanel() {
  isPanelOpen.value = false
}
</script><style scoped>
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
  font-size: 24px;
  color: #111827;
}

.icon-btn:hover {
  background: #f3f4f6;
}

.icon-btn:active {
  transform: scale(0.96);
}

.panel-overlay {
  position: fixed;
  inset: 0;
  z-index: 5000;
  background: rgba(15, 23, 42, 0.42);
  display: flex;
  justify-content: flex-end;
  align-items: stretch;
}

.panel {
  position: relative;
  width: min(380px, 92vw);
  height: 100dvh;
  max-height: 100dvh;
  background: #ffffff;
  box-shadow: -8px 0 24px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  z-index: 5001;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 18px 14px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: #111827;
}

.header-close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 10px;
  background: #f3f4f6;
  color: #111827;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.header-close-btn:hover {
  background: #e5e7eb;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 18px;
}

.empty-state {
  padding: 18px;
  border-radius: 14px;
  background: #f9fafb;
  color: #6b7280;
  text-align: center;
  border: 1px solid #e5e7eb;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-card {
  padding: 14px;
  border-radius: 14px;
  background: #f8fbff;
  border: 1px solid #dbe7f5;
}

.event-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.event-title {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: #111827;
  line-height: 1.3;
}

.badge {
  white-space: nowrap;
  padding: 5px 8px;
  border-radius: 999px;
  background: #dcfce7;
  color: #166534;
  font-size: 12px;
  font-weight: 700;
}

.event-address {
  margin: 0 0 8px;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.4;
}

.event-meta {
  margin: 4px 0;
  color: #374151;
  font-size: 14px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag {
  padding: 6px 10px;
  border-radius: 999px;
  background: #e8f1ff;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
}

.panel-footer {
  padding: 14px 18px 18px;
  border-top: 1px solid #e5e7eb;
}

.close-btn {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: none;
  background: #f63b3b;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s ease;
}

.close-btn:hover {
  background: #bb2c2c;
}

.close-btn:active {
  transform: scale(0.98);
}
</style>