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
          <button type="submit" :disabled="isLoading">
            {{ isLoading ? "Logging in..." : "Login" }}
          </button>
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

const email = ref("")
const password = ref("")
const error = ref<string | null>(null)
const isLoading = ref(false)

const router = useRouter()

type LoginResponse = {
  access_token: string
  token_type: string
}

function parseJwtPayload(token: string) {
  try {
    const base64Url = token.split(".")[1]
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/")
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    )
    return JSON.parse(jsonPayload)
  } catch {
    return null
  }
}

async function onSubmit() {
  error.value = null
  isLoading.value = true

  try {
    const form = new URLSearchParams()
    form.append("username", email.value)
    form.append("password", password.value)

    const response = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: form.toString()
    })

    if (!response.ok) {
      let message = "Login failed"
      try {
        const err = await response.json()
        message = err?.detail ?? message
      } catch {
        message = await response.text()
      }
      throw new Error(message)
    }

    const result: LoginResponse = await response.json()

    localStorage.setItem("token", result.access_token)
    localStorage.setItem("token_type", result.token_type)

    const payload = parseJwtPayload(result.access_token)
    if (payload?.sub) {
      localStorage.setItem("userId", String(payload.sub))
    }

    localStorage.setItem("userEmail", email.value)

    console.log("Saved token:", localStorage.getItem("token"))
    console.log("Saved userId:", localStorage.getItem("userId"))

    router.push({ name: "EventAdd" })
  } catch (err: any) {
    error.value = err?.message ?? String(err)
  } finally {
    isLoading.value = false
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
.helper { margin-top: 12px; }
</style>