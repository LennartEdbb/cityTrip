// src/stores/favourites.ts
import { ref } from "vue"

const LS_KEY = "citytrip:favourites:v1"
const favIds = ref<Set<string>>(new Set(load()))

function load(): string[] {
  try {
    const raw = localStorage.getItem(LS_KEY)
    const arr = raw ? JSON.parse(raw) : []
    return Array.isArray(arr) ? arr.map(String) : []
  } catch {
    return []
  }
}

function save() {
  localStorage.setItem(LS_KEY, JSON.stringify([...favIds.value]))
}

export function useFavourites() {
  function isFavourite(id: string) {
    return favIds.value.has(String(id))
  }

  function toggleFavourite(id: string) {
    const key = String(id)
    if (favIds.value.has(key)) favIds.value.delete(key)
    else favIds.value.add(key)
    save()
  }

  function setFavourite(id: string, on: boolean) {
    const key = String(id)
    if (on) favIds.value.add(key)
    else favIds.value.delete(key)
    save()
  }

  return { favIds, isFavourite, toggleFavourite, setFavourite }
}