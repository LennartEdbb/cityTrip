import { ref, watch } from "vue"
import { useAuth } from "@/store/auth"

const favIds = ref<Set<string>>(new Set())

export function useFavourites() {
  const auth = useAuth()
  const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000"

  async function fetchFavorites() {
    if (!auth.token.value) {
      favIds.value = new Set()
      return
    }

    try {
      const res = await fetch(`${API_BASE}/me/favorites`, {
        method: "GET",
        headers: { Authorization: `Bearer ${auth.token.value}`, Accept: "application/json" },
      })
      if (!res.ok) {
        favIds.value = new Set()
        return
      }
      const data = await res.json()
      // data: array of { id, aktivitaet_id, hinzugefuegt_am }
      const ids = Array.isArray(data) ? data.map((d: any) => String(d.aktivitaet_id ?? d.aktivitaetId ?? d.id)) : []
      favIds.value = new Set(ids)
    } catch (err) {
      favIds.value = new Set()
    }
  }

  async function toggleFavourite(id: string) {
    const key = String(id)
    if (!auth.token.value) {
      return
    }

    if (favIds.value.has(key)) {
      try {
        const res = await fetch(`${API_BASE}/me/favorites/${encodeURIComponent(key)}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${auth.token.value}` },
        })
        if (res.ok) favIds.value.delete(key)
      } catch {
      }
    } else {
      try {
        const res = await fetch(`${API_BASE}/me/favorites/${encodeURIComponent(key)}`, {
          method: "POST",
          headers: { Authorization: `Bearer ${auth.token.value}` },
        })
        if (res.ok) favIds.value.add(key)
      } catch {
      }
    }
  }

  function isFavourite(id: string) {
    return favIds.value.has(String(id))
  }

  watch(
    () => auth.token.value,
    (t) => {
      if (t) fetchFavorites()
      else favIds.value = new Set()
    },
    { immediate: true }
  )

  return { favIds, isFavourite, toggleFavourite, fetchFavorites }
}