<template>
  <div class="settings-view">
    <header class="settings-head">
      <div>
        <p class="settings-eyebrow">Account</p>
        <h1 class="settings-title">My Profile</h1>

        <p v-if="token" class="settings-sub">
          Logged in as <strong>{{ currentUser?.name || "—" }}</strong>
        </p>
        <p v-else class="settings-sub">
          Manage your profile and account access.
        </p>
      </div>

      <div class="settings-head-icon">
        <span class="material-icons">person</span>
      </div>
    </header>

    <div class="settings-root">
      <div class="settings-stack">
        <div class="card">
          <template v-if="!token">
            <div class="empty-state">
              <div class="empty-icon">
                <span class="material-icons">person_off</span>
              </div>

              <div class="empty-title">You are not logged in</div>
              <div class="empty-sub">
                Log in to view your profile and manage your account.
              </div>

              <div class="row">
                <router-link to="/login" class="link-reset">
                  <button class="primary-btn" type="button">Login</button>
                </router-link>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="profile-top">
              <div class="avatar">
                {{ (local.name || currentUser?.email || "U").charAt(0).toUpperCase() }}
              </div>

              <div>
                <div class="profile-title">{{ local.name || "Your profile" }}</div>
                <div class="muted">{{ local.email || "—" }}</div>
              </div>
            </div>

            <div class="form-grid">
              <div class="field">
                <label for="name">Name</label>
                <input id="name" v-model="local.name" placeholder="Your name" readonly />
              </div>

              <div class="field">
                <label for="email">Email</label>
                <input id="email" v-model="local.email" placeholder="name@example.com" readonly />
              </div>

              <div class="field">
                <label for="rolle">Role</label>
                <input id="rolle" :value="local.rolle || '-'" readonly />
              </div>

              <div class="field">
                <label>User ID</label>
                <div class="muted">{{ currentUser?.id ?? "-" }}</div>
              </div>
            </div>

            <div class="actions">
              <button class="primary-btn" type="button" @click="doLogout">
                Logout
              </button>
            </div>

            <div v-if="msg" class="msg">{{ msg }}</div>
          </template>
        </div>

        <div v-if="token && isAnbieter" class="card">
          <div class="section-head">
            <div>
              <p class="settings-eyebrow">Events</p>
              <h2 class="section-title">My events</h2>
            </div>

            <div class="section-icon">
              <span class="material-icons">event</span>
            </div>
          </div>

          <template v-if="!currentUser">
            <div class="empty-state slim">
              You are not logged in.
            </div>
          </template>

          <template v-else-if="ownEvents.length === 0">
            <div class="empty-state slim">
              No own events found.
            </div>
          </template>

          <template v-else>
            <div class="event-list">
              <article
                v-for="event in ownEvents"
                :key="event.id"
                class="event-card"
              >
                <div class="event-card-top">
                  <div>
                    <h3 class="event-title">{{ event.name }}</h3>
                    <p v-if="event.creatorName" class="event-meta">
                      <strong>Creator:</strong> {{ event.creatorName }}
                    </p>
                  </div>

                  <div class="event-actions">
                    <span v-if="event.accessible" class="badge">Accessible</span>

                    <button
                      class="delete-btn"
                      type="button"
                      :disabled="deletingId === event.id"
                      :title="deletingId === event.id ? 'Deleting...' : 'Delete event'"
                      @click="deleteEvent(event)"
                    >
                      <span class="material-icons">delete</span>
                    </button>
                  </div>
                </div>

                <p class="event-address">{{ event.address }}</p>

                <p v-if="event.whenText" class="event-meta">
                  <strong>When:</strong> {{ event.whenText }}
                </p>

                <p v-if="event.priceText" class="event-meta">
                  <strong>Price:</strong> {{ event.priceText }}
                </p>

                <p class="event-meta">
                  <strong>Creator ID:</strong> {{ event.creatorId ?? "-" }}
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
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { useAuth } from "@/store/auth"

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
  creatorName?: string
}

const props = defineProps<{
  events?: Venue[]
}>()

const emit = defineEmits<{
  (e: "event-deleted", id: string): void
}>()

const auth = useAuth()
const router = useRouter()

const token = auth.token
const currentUser = auth.currentUser

const msg = ref<string | null>(null)
const deletingId = ref<string | null>(null)

const local = reactive({
  name: "",
  email: "",
  rolle: "",
})

watch(
  () => auth.currentUser.value,
  (u) => {
    if (u) {
      local.name = u.name ?? ""
      local.email = u.email ?? ""
      local.rolle = (u as any).rolle ?? ""
    } else {
      local.name = ""
      local.email = ""
      local.rolle = ""
    }
  },
  { immediate: true }
)

const isAnbieter = computed(() => {
  return String(currentUser.value?.rolle ?? "").toLowerCase() === "anbieter"
})

const ownEvents = computed(() => {
  const userId = currentUser.value?.id

  if (userId === undefined || userId === null) {
    return []
  }

  return (props.events ?? []).filter((event) => {
    return String(event.creatorId) === String(userId)
  })
})

async function deleteEvent(event: Venue) {
  if (!event?.id) return

  const confirmed = window.confirm(`Delete event "${event.name}"?`)
  if (!confirmed) return

  deletingId.value = event.id
  msg.value = null

  try {
    const API_BASE =
      (import.meta as any).env?.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000"

    const headers: Record<string, string> = {
      Accept: "application/json",
    }

    const authToken = auth.token?.value
    if (authToken) {
      headers.Authorization = `Bearer ${authToken}`
    }

    const res = await fetch(`${API_BASE}/activities/${event.id}`, {
      method: "DELETE",
      mode: "cors",
      headers,
    })

    if (!res.ok) {
      const text = await res.text().catch(() => "")
      throw new Error(`DELETE failed: ${res.status} ${res.statusText} ${text}`)
    }

    msg.value = `Event "${event.name}" deleted.`
    emit("event-deleted", event.id)
  } catch (err) {
    console.error("Failed to delete event:", err)
    msg.value = "Could not delete event."
  } finally {
    deletingId.value = null
    window.setTimeout(() => {
      msg.value = null
    }, 2500)
  }
}

function doLogout() {
  auth.logout()
  router.push({ name: "Map" })
}
</script>

<style scoped>
.settings-view {
  min-height: 100%;
  padding: 18px 16px 120px;
  background:
    radial-gradient(
      circle at top right,
      rgba(59, 130, 246, 0.12) 0%,
      rgba(59, 130, 246, 0.06) 32%,
      transparent 52%
    ),
    linear-gradient(180deg, #f8fbff 0%, #ffffff 240px);
}

input[readonly] {
  background: #f9fafb;
  color: rgba(17, 24, 39, 0.72);
  cursor: default;
}

.settings-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  padding: 4px 2px 8px;
}

.settings-eyebrow {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(17, 24, 39, 0.5);
}

.settings-title {
  margin: 0;
  font-size: 24px;
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.03em;
  color: #111827;
}

.settings-sub {
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(17, 24, 39, 0.62);
  font-weight: 700;
}

.settings-head-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  background: linear-gradient(180deg, #e0ecff 0%, #c7dbff 100%);
  border: 1px solid rgba(59, 130, 246, 0.14);
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.14);
}

.settings-head-icon .material-icons {
  font-size: 22px;
  color: #2563eb;
}

.settings-root {
  display: grid;
  place-items: start center;
}

.settings-stack {
  width: min(720px, 100%);
  display: grid;
  gap: 16px;
}

.card {
  width: 100%;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(17, 24, 39, 0.07);
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 16px 40px rgba(17, 24, 39, 0.08);
  backdrop-filter: blur(10px);
}

.profile-top {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(17, 24, 39, 0.06);
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 18px;
  font-weight: 900;
  color: #1d4ed8;
  background: linear-gradient(180deg, #eaf2ff 0%, #dbeafe 100%);
  border: 1px solid rgba(59, 130, 246, 0.12);
}

.profile-title {
  font-size: 16px;
  font-weight: 900;
  color: #111827;
  line-height: 1.2;
}

.form-grid {
  display: grid;
  gap: 14px;
}

.field {
  display: grid;
  gap: 6px;
}

label {
  font-size: 13px;
  font-weight: 800;
  color: #111827;
}

input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(17, 24, 39, 0.1);
  background: #ffffff;
  color: #111827;
  font-size: 14px;
  outline: none;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
  box-sizing: border-box;
}

input::placeholder {
  color: rgba(17, 24, 39, 0.38);
}

input:focus {
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.primary-btn,
.secondary-btn {
  appearance: none;
  border: 0;
  border-radius: 14px;
  padding: 11px 16px;
  font-weight: 800;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.primary-btn {
  background: #2563eb;
  color: #ffffff;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.22);
}

.primary-btn:hover {
  transform: translateY(-1px);
  background: #1d4ed8;
}

.secondary-btn {
  background: #ffffff;
  color: #111827;
  border: 1px solid rgba(17, 24, 39, 0.08);
}

.secondary-btn:hover {
  transform: translateY(-1px);
  background: rgba(17, 24, 39, 0.03);
}

.muted {
  color: rgba(17, 24, 39, 0.58);
  font-size: 13px;
  font-weight: 700;
}

.msg {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(16, 185, 129, 0.1);
  color: #065f46;
  font-size: 13px;
  font-weight: 800;
}

.row {
  margin-top: 16px;
}

.link-reset {
  text-decoration: none;
}

.empty-state {
  text-align: center;
  padding: 10px 6px 2px;
}

.empty-state.slim {
  padding: 18px;
  border-radius: 14px;
  background: #f9fafb;
  color: #6b7280;
  text-align: center;
  border: 1px solid #e5e7eb;
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 14px;
  border-radius: 20px;
  display: grid;
  place-items: center;
  background: linear-gradient(180deg, #eef4ff 0%, #dbeafe 100%);
  border: 1px solid rgba(59, 130, 246, 0.12);
}

.empty-icon .material-icons {
  font-size: 30px;
  color: #2563eb;
}

.empty-title {
  font-size: 18px;
  font-weight: 900;
  color: #111827;
}

.empty-sub {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.45;
  color: rgba(17, 24, 39, 0.62);
  font-weight: 700;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  color: #111827;
}

.section-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: linear-gradient(180deg, #eef4ff 0%, #dbeafe 100%);
  border: 1px solid rgba(59, 130, 246, 0.12);
}

.section-icon .material-icons {
  font-size: 22px;
  color: #2563eb;
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
</style>