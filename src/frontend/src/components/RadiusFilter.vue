<template>
  <div class="radius-filter">
    <label for="radius-slider">Radius: {{ radius }} km</label>
    <input
      id="radius-slider"
      type="range"
      min="1"
      max="50"
      v-model="radius"
      @input="onRadiusChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const radius = ref(10) // default 10 km

const emit = defineEmits<{
  radiusChange: [value: number]
}>()

function onRadiusChange() {
  emit('radiusChange', radius.value)
}
</script>

<style scoped>
.radius-filter {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 14px;
  font-weight: 600;
}

input[type="range"] {
  width: 100%;
}
</style>