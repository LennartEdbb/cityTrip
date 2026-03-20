<template>
  <div class="auth-page">
    <div class="bg-shape bg-shape-1"></div>
    <div class="bg-shape bg-shape-2"></div>

    <div class="card">
      <div class="card-header">
        <p class="eyebrow">Welcome back</p>
        <h2>Login</h2>
        <p class="subtitle">Sign in to continue to your account.</p>
      </div>

      <form class="form" @submit.prevent="onSubmit">
        <div class="field">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            inputmode="email"
            autocomplete="email"
            placeholder="you@example.com"
            required
          />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="Enter your password"
            required
          />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <div class="actions">
          <button class="primary" type="submit">Login</button>
          <button class="secondary" type="button" @click="goHome">Cancel</button>
        </div>
        <div class="helper">
          <span>Don’t have an account?</span>
          <router-link to="/register">Create one</router-link>
        </div>
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
:global(*) {
  box-sizing: border-box;
}

.auth-page {
  position: relative;
  min-height: 100svh;
  display: grid;
  place-items: center;
  padding: 20px 16px;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(47, 91, 255, 0.12), transparent 35%),
    radial-gradient(circle at bottom right, rgba(139, 92, 246, 0.14), transparent 30%),
    linear-gradient(180deg, #f8faff 0%, #eef2ff 100%);
}

.bg-shape {
  position: absolute;
  border-radius: 999px;
  filter: blur(10px);
  pointer-events: none;
}

.bg-shape-1 {
  width: 220px;
  height: 220px;
  top: -60px;
  left: -80px;
  background: rgba(47, 91, 255, 0.12);
}

.bg-shape-2 {
  width: 180px;
  height: 180px;
  right: -60px;
  bottom: -40px;
  background: rgba(168, 85, 247, 0.12);
}

.card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
  border-radius: 24px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow:
    0 20px 50px rgba(30, 41, 59, 0.12),
    0 6px 16px rgba(30, 41, 59, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.7);
}

.card-header {
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0 0 6px;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #2f5bff;
}

h2 {
  margin: 0;
  font-size: clamp(1.75rem, 4vw, 2.1rem);
  line-height: 1.1;
  color: #0f172a;
}

.subtitle {
  margin: 10px 0 0;
  color: #64748b;
  font-size: 0.96rem;
  line-height: 1.5;
}

.form {
  display: grid;
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
}

label {
  font-size: 0.94rem;
  font-weight: 700;
  color: #1e293b;
}

input {
  width: 100%;
  min-height: 48px;
  padding: 13px 14px;
  border-radius: 14px;
  border: 1px solid #dbe2ea;
  background: #fff;
  color: #0f172a;
  font-size: 16px; /* prevents iOS zoom */
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
}

input::placeholder {
  color: #94a3b8;
}

input:focus {
  border-color: #2f5bff;
  box-shadow: 0 0 0 4px rgba(47, 91, 255, 0.12);
}

.actions {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin-top: 4px;
}

button {
  min-height: 48px;
  width: 100%;
  border-radius: 14px;
  border: none;
  font-size: 0.98rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

button:hover {
  transform: translateY(-1px);
}

button:active {
  transform: translateY(0);
}

.primary {
  background: linear-gradient(135deg, #2f5bff 0%, #4f7cff 100%);
  color: #fff;
  box-shadow: 0 10px 20px rgba(47, 91, 255, 0.22);
}

.secondary {
  background: rgba(255, 255, 255, 0.85);
  color: #0f172a;
  border: 1px solid #dbe2ea;
}

.helper {
  margin-top: 4px;
  text-align: center;
  font-size: 0.95rem;
  color: #64748b;
  line-height: 1.5;
}

.helper a {
  margin-left: 6px;
  font-weight: 700;
  color: #2f5bff;
  text-decoration: none;
}

.helper a:hover {
  text-decoration: underline;
}

.error {
  border-radius: 14px;
  padding: 12px 14px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 0.94rem;
  font-weight: 600;
}

@media (min-width: 640px) {
  .auth-page {
    padding: 32px 20px;
  }

  .card {
    padding: 32px;
  }

  .actions {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 380px) {
  .card {
    padding: 20px 16px;
    border-radius: 20px;
  }

  h2 {
    font-size: 1.55rem;
  }

  .subtitle,
  .helper {
    font-size: 0.9rem;
  }
}
</style>