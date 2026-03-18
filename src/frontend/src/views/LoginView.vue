<template>
  <div class="auth-page">
    <div class="card">
      <h2>Login</h2>
      <form @submit.prevent="onSubmit">
        <label>Email</label>
        <input v-model="email" type="email" required />
        <label>Password</label>
        <input v-model="password" type="password" required />
        <div class="actions">
          <button type="submit">Login</button>
          <button type="button" @click="goHome">Cancel</button>
        </div>
        <div class="helper">
          <router-link to="/register">Register a new account</router-link>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuth } from "@/store/auth"

const email = ref("")
const password = ref("")
const error = ref<string | null>(null)

const router = useRouter()
const auth = useAuth()

async function onSubmit() {
  error.value = null
  try {
    await auth.login(email.value, password.value)
    router.push({ name: "Map" })
  } catch (err: any) {
    error.value = err?.message ?? String(err)
  }
}

function goHome() {
  router.push({ name: "Map" })
}
</script>

<style scoped>
.auth-page {
  display: grid;
  place-items: center;
  height: 100vh;
  background: #f7f8fc;
}
.card {
  width: min(420px, 92vw);
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 18px 45px rgba(0,0,0,0.08);
}
label { display:block; margin-top:10px; font-weight:700; }
input { width:100%; padding:8px 10px; margin-top:6px; border-radius:8px; border:1px solid #e5e7eb }
.actions { display:flex; gap:8px; margin-top:12px }
button { padding:10px 14px; border-radius:10px; border:0; background:#2f5bff; color:#fff; font-weight:700 }
button[type="button"]{ background:#fff; color:#111; border:1px solid rgba(17,24,39,0.08) }
.error { margin-top:12px; color:#b91c1c; font-weight:700 }
</style>
