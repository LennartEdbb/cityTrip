<template>
  <div class="settings-root">
    <div class="card">
      <h2>Settings & Profile</h2>

      <div v-if="!token">
        <p>You are not logged in.</p>
        <div class="row">
          <router-link to="/login"><button>Login</button></router-link>
        </div>
      </div>

      <div v-else>
        <p class="muted">Logged in as <strong>{{ currentUser?.email || '—' }}</strong></p>

        <label>Name</label>
        <input v-model="local.name" />

        <!-- <label>Email</label>
        <input v-model="local.email" />

        <label>Role</label>
        <input v-model="local.rolle" /> -->

        <div class="actions">
          <button @click="save">Save (local)</button>
          <button @click="doLogout" class="secondary">Logout</button>
        </div>

        <div v-if="msg" class="msg">{{ msg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { useAuth } from "@/store/auth"

const auth = useAuth()
const token = auth.token
const currentUser = auth.currentUser
const router = useRouter()
const msg = ref<string | null>(null)

const local = reactive({ name: "", email: "", rolle: "" })

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

async function save() {
  msg.value = null
  // Try to update on server; fallback to local save
  try {
    const res = await auth.updateProfile({ name: local.name, email: local.email, rolle: local.rolle })
    if (res) {
      msg.value = "Saved to server"
    } else {
      msg.value = "Saved locally"
    }
  } catch (err: any) {
    auth.setProfile({ name: local.name, email: local.email, rolle: local.rolle })
    msg.value = "Saved locally"
  }

  setTimeout(() => (msg.value = null), 2000)
}

function doLogout() {
  auth.logout()
  router.push({ name: "Map" })
}
</script>

<style scoped>
.settings-root { padding: 20px; display:grid; place-items:center }
.card { width: min(720px, 96vw); background:white; padding:18px; border-radius:12px; box-shadow:0 18px 45px rgba(0,0,0,0.06) }
label { display:block; margin-top:10px; font-weight:700 }
input { width:100%; padding:8px 10px; margin-top:6px; border-radius:8px; border:1px solid #e5e7eb }
.actions { display:flex; gap:8px; margin-top:12px }
button { padding:8px 12px; border-radius:8px; border:0; background:#2f5bff; color:#fff; font-weight:700 }
button.secondary { background:#fff; color:#111; border:1px solid rgba(17,24,39,0.08) }
.muted { color: rgba(17,24,39,0.6); font-weight:700 }
.msg { margin-top:10px; color:#065f46; font-weight:700 }
.row { margin-top:12px }
</style>
