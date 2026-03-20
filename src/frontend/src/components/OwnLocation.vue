<template>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"

const emit = defineEmits<{
  "location-obtained": [position: GeolocationPosition]
}>()

const message = ref("")
const loading = ref(false)

function getLocation() {
  if (!navigator.geolocation) {
    message.value = "Geolocation is not supported by this browser."
    return
  }

  loading.value = true
  message.value = "Getting your location..."
  navigator.geolocation.getCurrentPosition(success, error)
}

function success(position: GeolocationPosition) {
  loading.value = false
  message.value = `Latitude: ${position.coords.latitude}
Longitude: ${position.coords.longitude}`

  emit("location-obtained", position)
}

function error() {
  loading.value = false
  message.value = "Sorry, no position available."
}

// Auto-get location on mount
onMounted(() => {
  getLocation()
})
</script>