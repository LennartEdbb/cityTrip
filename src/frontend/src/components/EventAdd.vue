<template>
  <div class="event-form">
    <input
      v-model="event.name"
      type="text"
      placeholder="Event Name"
    />

    <input
      v-model="event.location"
      type="text"
      placeholder="Event Location"
    />

    <input
      v-model="event.date"
      type="datetime-local"
    />

    <div class="dd-categorie">
      <select v-model="event.category">
        <option value="culture">Culture</option>
        <option value="sport">Sport</option>
        <option value="food">Food</option>
        <option value="music">Music</option>
        <option value="other">Other</option>
      </select>
    </div>

    <button @click="addEvent">Add Event</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"

type EventItem = {
  name: string
  location: string
  date: string
  category: string
}

const event = ref<EventItem>({
  name: "",
  location: "",
  date: "",
  category: "culture"
})

async function addEvent() {
  if (!event.value.name || !event.value.location || !event.value.date) {
    alert("Please fill all fields")
    return
  }

  try {
    const response = await fetch("http://localhost:3000/api/v1/events", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(event.value)
    })

    if (!response.ok) {
      throw new Error("Failed to save event")
    }

    const result = await response.json()
    console.log("Event saved:", result)

    alert("Event added successfully!")

    event.value = {
      name: "",
      location: "",
      date: "",
      category: "culture"
    }

  } catch (error) {
    console.error(error)
    alert("Error adding event")
  }
}
</script>

<style scoped>
.event-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
}
</style>
