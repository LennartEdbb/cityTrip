<template>
  <div class="auth-page">
    <div class="card">
      <h2>Register</h2>
      <form @submit.prevent="onSubmit">
        <label>Name</label>
        <input v-model="name" required />
        <label>Email</label>
        <input v-model="email" type="email" required />
        <label>Password</label>
        <input v-model="password" type="password" required />
        <div class="actions">
          <button type="submit">Register</button>
          <button type="button" @click="goLogin">Cancel</button>
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div v-if="msg" class="msg">{{ msg }}</div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuth } from "@/store/auth"

const name = ref("")
const email = ref("")
const password = ref("")
const error = ref<string | null>(null)
const msg = ref<string | null>(null)

const router = useRouter()
const auth = useAuth()

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000"

async function onSubmit() {
  error.value = null
  msg.value = null
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ name: name.value, email: email.value, password: password.value }),
    })

    if (!res.ok) {
      const text = await res.text().catch(() => "")
      throw new Error(`Register failed: ${res.status} ${res.statusText} ${text}`)
    }

    msg.value = "Registration successful — you can now log in"
    // optionally auto-login
    try {
      await auth.login(email.value, password.value)
      router.push({ name: "Map" })
      return
    } catch {
      router.push({ name: "Login" })
      return
    }
  } catch (err: any) {
    error.value = err?.message ?? String(err)
  }
}

function goLogin() {
  router.push({ name: "Login" })
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
.msg { margin-top:12px; color:#065f46; font-weight:700 }
</style>
