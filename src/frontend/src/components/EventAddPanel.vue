<template>
  <button 
    class="icon-btn" 
    aria-label="Menu"
    @click="openPanel"
  >
    +
  </button>

  <div v-if="isPanelOpen" class="panel">
    <div class="panel-content">
        

      Empty space for cool content


      <button class="close-btn" @click="closePanel">Close</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const isPanelOpen = ref(false)

function openPanel() {
    isPanelOpen.value = true
}

function closePanel() {
    console.log("close")
    isPanelOpen.value = false
}
</script>

<style>
.icon-btn {
    font-size: 24px;
    width: 40px;
    height: 40px;
    cursor: pointer;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 50%;
}

.panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 300px;
    height: 100%;
    background: white;
    box-shadow: -2px 0 10px rgba(0,0,0,0.2);
    padding: 20px;
}

.close-btn {
  margin-top: 6px;
  padding: 11px;
  border-radius: 8px;
  border: none;
  background: #f63b3b;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s ease;
}

.close-btn:hover {
  background: #bb2c2c;
}

.close-btn:active {
  transform: scale(0.98);
}
</style>
