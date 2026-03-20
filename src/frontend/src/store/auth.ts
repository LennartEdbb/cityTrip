import { ref } from "vue"

const LS_KEY = "citytrip:auth:v1"

type User = { id?: number; name?: string; email?: string; rolle?: string }

const token = ref<string | null>(null)
const currentUser = ref<User | null>(null)

function load() {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (!raw) return
    const obj = JSON.parse(raw)
    token.value = obj.token ?? null
    currentUser.value = obj.user ?? null
  } catch {
    token.value = null
    currentUser.value = null
  }
}

function save() {
  const obj = { token: token.value, user: currentUser.value }
  localStorage.setItem(LS_KEY, JSON.stringify(obj))
}

load()

export function useAuth() {
  const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000"

  async function login(email: string, password: string) {
    // Try OAuth2 password grant (form encoded)
    const url = `${API_BASE}/auth/login`
    const body = new URLSearchParams()
    body.append("username", email)
    body.append("password", password)

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    })

    if (!res.ok) {
      const text = await res.text().catch(() => "")
      throw new Error(`Login failed: ${res.status} ${res.statusText} ${text}`)
    }

    const data = await res.json().catch(() => ({}))
    const t = data?.access_token ?? data?.token ?? null
    if (!t) throw new Error("Server did not return access token")
    token.value = String(t)
    save()

    await fetchProfile()
    return true
  }

  async function fetchProfile() {
    if (!token.value) return null
    try {
      const res = await fetch(`${API_BASE}/me/profile`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token.value}`, Accept: "application/json" },
      })
      if (!res.ok) return null
      const data = await res.json()
      currentUser.value = data ?? null
      save()
      return currentUser.value
    } catch {
      return null
    }
  }

  function logout() {
    token.value = null
    currentUser.value = null
    save()
  }

  function setProfile(p: Partial<User>) {
    currentUser.value = Object.assign({}, currentUser.value ?? {}, p)
    save()
  }

  async function updateProfile(updates: Partial<User>) {
    if (!token.value) {
      setProfile(updates)
      return null
    }

    try {
      const res = await fetch(`${API_BASE}/me/profile`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token.value}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(updates),
      })

      if (!res.ok) {
        const text = await res.text().catch(() => "")
        throw new Error(`Profile update failed: ${res.status} ${res.statusText} ${text}`)
      }

      const data = await res.json().catch(() => null)
      if (data) {
        currentUser.value = data
        save()
        return currentUser.value
      }
    } catch (err) {
      // fallback to local
      setProfile(updates)
      return null
    }
  }

  return { token, currentUser, login, logout, fetchProfile, setProfile, updateProfile }
}
