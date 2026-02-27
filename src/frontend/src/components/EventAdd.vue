<template>
  <div class="event-form">
    <input v-model="event.name" type="text" placeholder="Event Name" />

    <div class="row">
      <input v-model="event.street" type="text" placeholder="Street" />
      <input v-model="event.number" type="text" placeholder="No." class="small" />
    </div>

    <div class="row">
      <input v-model="event.zipcode" type="text" placeholder="Zipcode" class="small" />
      <input v-model="event.city" type="text" placeholder="City" />
    </div>

    <input v-model="event.date" type="datetime-local" />

    <select v-model="event.type">
      <option value="einmalig">Einmalig</option>
      <option value="dauerhaft">Dauerhaft</option>
    </select>

    <select v-model="event.category">
      <option disabled value="">Select category</option>
      <option value="sport">Sport</option>
      <option value="food">Food</option>
      <option value="music">Music</option>
      <option value="other">Other</option>
    </select>

    <button @click="addEvent">Add Event</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"

type EventItem = {
    name: string
    street: string
    number: string
    zipcode: string
    city: string
    date: string
    category: string
    type: 'einmalig' | 'dauerhaft'
}

const event = ref<EventItem>({
    name: "",
    street: "",
    number: "",
    zipcode: "",
    city: "",
    date: "",
    category: "category",
    type: "einmalig"
})

async function addEvent() {
  if (!event.value.name || !event.value.street|| !event.value.number || !event.value.zipcode || !event.value.city || !event.value.date) {
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
        street: "",
        number: "",
        zipcode: "",
        city: "",
        date: "",
        category: "category",
        type: "einmalig"
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
  gap: 14px;
}

.row {
  display: flex;
  gap: 12px;
}

.small {
  max-width: 110px;
}

input,
select {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  font-size: 14px;
  background: #fff;
  transition: all 0.2s ease;
}

input:focus,
select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

button {
  margin-top: 6px;
  padding: 11px;
  border-radius: 8px;
  border: none;
  background: #3b82f6;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s ease;
}

button:hover {
  background: #2563eb;
}

button:active {
  transform: scale(0.98);
}
</style>