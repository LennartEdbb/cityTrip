<template>
  <section class="event-page">
    <div class="event-shell">
      <header class="page-header">
        <p class="eyebrow">Eventverwaltung</p>
        <h1>Neues Event anlegen</h1>
      </header>

      <form class="event-form" @submit.prevent="addEvent">
        <section class="form-section">
          <h2>Allgemein</h2>

          <input
            v-model="event.bezeichnung"
            type="text"
            placeholder="Eventname"
          />

          <textarea
            v-model="event.beschreibung"
            placeholder="Beschreibung"
          />
          <textarea v-model="event.bemerkung" placeholder="Bemerkung" />

          <select v-model="selectedCategory">
            <option disabled value="">Kategorie auswählen</option>
            <option value="Bildung">Bildung</option>
            <option value="Sport">Sport</option>
            <option value="Musik">Musik</option>
            <option value="Essen">Essen</option>
            <option value="Sonstiges">Sonstiges</option>
          </select>

          <div class="checkbox-row">
            <label class="checkbox-card">
              <input v-model="event.barrierefrei" type="checkbox" />
              <span>Barrierefrei</span>
            </label>

            <label class="checkbox-card">
              <input v-model="event.aktiv" type="checkbox" />
              <span>Aktiv</span>
            </label>
          </div>
        </section>

        <section class="form-section">
          <h2>Ort</h2>

          <div class="grid-2">
            <input
              v-model="event.location.bezeichnung"
              type="text"
              placeholder="Ort / Location"
            />
            <input
              v-model="event.location.bemerkung"
              type="text"
              placeholder="Hinweis zum Ort"
            />
          </div>

          <textarea
            v-model="event.location.beschreibung"
            placeholder="Beschreibung des Ortes"
          />

          <div class="grid-2">
            <input
              v-model="event.location.anschrift.strasse"
              type="text"
              placeholder="Straße"
            />
            <input
              v-model="event.location.anschrift.hausnummer"
              type="text"
              placeholder="Nr."
            />
          </div>

          <div class="grid-2">
            <input
              v-model="event.location.anschrift.plz"
              type="text"
              placeholder="PLZ"
            />
            <input
              v-model="event.location.anschrift.ort"
              type="text"
              placeholder="Ort"
            />
          </div>

          <input
            v-model="event.location.anschrift.land"
            type="text"
            placeholder="Land"
          />

          <div class="grid-2">
            <input
              v-model.number="event.location.lat"
              type="number"
              step="any"
              placeholder="Breitengrad"
            />
            <input
              v-model.number="event.location.lon"
              type="number"
              step="any"
              placeholder="Längengrad"
            />
          </div>
        </section>

        <section class="form-section">
          <h2>Zeit</h2>

          <select v-model="event.zeitmodell.typ">
            <option value="einmalig">Einmalig</option>
            <option value="dauerhaft">Dauerhaft</option>
          </select>

          <input v-model="event.zeitmodell.datum" type="date" />

          <div class="grid-2">
            <input v-model="event.zeitmodell.von" type="time" />
            <input v-model="event.zeitmodell.bis" type="time" />
          </div>

          <input
            v-model="event.zeitmodell.hinweis"
            type="text"
            placeholder="Hinweis zur Zeit"
          />
        </section>

        <section class="form-section">
          <h2>Eintritt</h2>

          <select v-model="event.eintritt.kostenmodell">
            <option value="Kostenlos">Kostenlos</option>
            <option value="Kostenpflichtig">Kostenpflichtig</option>
          </select>

          <input
            v-model="event.eintritt.hinweis"
            type="text"
            placeholder="Hinweis zum Eintritt"
          />

          <div
            v-if="event.eintritt.kostenmodell === 'Kostenpflichtig'"
            class="tarif-box"
          >
          </div>
        </section>

        <div class="button-row">
          <button type="button" class="secondary" @click="fillTestData">
            Testdaten einfügen
          </button>

          <button type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? "Speichert..." : "Event hinzufügen" }}
          </button>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"

type Tarif = {
  bezeichnung: string
  dauer_typ: "Stunde" | "Tag" | "Woche" | "Monat"
  dauer_wert: number
  preis: number
  kriterium: string
  waehrung: "Euro"
}

type ActivityPayload = {
  bezeichnung: string
  beschreibung: string
  bemerkung: string
  kategorien: string[]
  barrierefrei: boolean
  aktiv: boolean
  location: {
    bezeichnung: string
    beschreibung: string
    bemerkung: string
    anschrift: {
      strasse: string
      hausnummer: string
      ort: string
      plz: string
      land: string
    }
    lat: number
    lon: number
  }
  zeitmodell: {
    typ: "einmalig" | "dauerhaft"
    datum: string
    von: string
    bis: string
    hinweis: string
  }
  eintritt: {
    kostenmodell: "Kostenlos" | "Kostenpflichtig"
    hinweis: string
    tarife: Tarif[]
  }
}

function createEmptyEvent(): ActivityPayload {
  return {
    bezeichnung: "",
    beschreibung: "",
    bemerkung: "",
    kategorien: [],
    barrierefrei: false,
    aktiv: true,
    location: {
      bezeichnung: "",
      beschreibung: "",
      bemerkung: "",
      anschrift: {
        strasse: "",
        hausnummer: "",
        ort: "",
        plz: "",
        land: "Deutschland"
      },
      lat: 0,
      lon: 0
    },
    zeitmodell: {
      typ: "einmalig",
      datum: "",
      von: "",
      bis: "",
      hinweis: ""
    },
    eintritt: {
      kostenmodell: "Kostenlos",
      hinweis: "",
      tarife: []
    }
  }
}

const event = ref<ActivityPayload>(createEmptyEvent())
const selectedCategory = ref("")
const isSubmitting = ref(false)

watch(selectedCategory, (value) => {
  event.value.kategorien = value ? [value] : []
})

watch(
  () => event.value.eintritt.kostenmodell,
  (value) => {
    if (value === "Kostenlos") {
      event.value.eintritt.tarife = []
    } else if (event.value.eintritt.tarife.length === 0) {
      event.value.eintritt.tarife = [
        {
          bezeichnung: "",
          dauer_typ: "Stunde",
          dauer_wert: 1,
          preis: 0,
          kriterium: "",
          waehrung: "Euro"
        }
      ]
    }
  },
  { immediate: true }
)

function fillTestData() {
  selectedCategory.value = "Musik"

  event.value = {
    bezeichnung: "Testkonzert Bielefeld",
    beschreibung:
      "Ein Testevent für die API – Live-Musik in entspannter Atmosphäre in Bielefeld.",
    bemerkung: "Bitte ignorieren – Testeintrag",
    kategorien: ["Musik"],
    barrierefrei: true,
    aktiv: true,
    location: {
      bezeichnung: "Lokschuppen Bielefeld",
      beschreibung: "Veranstaltungsort für Konzerte und Events in Bielefeld",
      bemerkung: "Zentrale Lage, gute Erreichbarkeit",
      anschrift: {
        strasse: "Stadtheider Straße",
        hausnummer: "11",
        ort: "Bielefeld",
        plz: "33609",
        land: "Deutschland"
      },
      lat: 52.0302,
      lon: 8.5325
    },
    zeitmodell: {
      typ: "einmalig",
      datum: "2026-04-01",
      von: "19:00",
      bis: "22:00",
      hinweis: "Einlass ab 18:30"
    },
    eintritt: {
      kostenmodell: "Kostenpflichtig",
      hinweis: "Tickets online erhältlich",
      tarife: [
        {
          bezeichnung: "Standardticket",
          dauer_typ: "Stunde",
          dauer_wert: 3,
          preis: 18.5,
          kriterium: "Erwachsene",
          waehrung: "Euro"
        }
      ]
    }
  }
}

function toIsoTime(date: string, time: string) {
  if (!date || !time) return ""
  return new Date(`${date}T${time}:00`).toISOString()
}

async function addEvent() {
  if (isSubmitting.value) return

  const required =
    event.value.bezeichnung &&
    event.value.location.bezeichnung &&
    event.value.location.anschrift.strasse &&
    event.value.location.anschrift.hausnummer &&
    event.value.location.anschrift.plz &&
    event.value.location.anschrift.ort &&
    event.value.location.anschrift.land &&
    event.value.zeitmodell.datum &&
    event.value.zeitmodell.von &&
    event.value.zeitmodell.bis &&
    event.value.kategorien.length > 0

  if (!required) {
    alert("Bitte alle Pflichtfelder ausfüllen")
    return
  }

  const payload = {
    bezeichnung: event.value.bezeichnung,
    beschreibung: event.value.beschreibung,
    bemerkung: event.value.bemerkung,
    kategorien: event.value.kategorien,
    barrierefrei: event.value.barrierefrei,
    aktiv: event.value.aktiv,
    location: {
      bezeichnung: event.value.location.bezeichnung,
      beschreibung: event.value.location.beschreibung,
      bemerkung: event.value.location.bemerkung,
      anschrift: {
        strasse: event.value.location.anschrift.strasse,
        hausnummer: event.value.location.anschrift.hausnummer,
        ort: event.value.location.anschrift.ort,
        plz: event.value.location.anschrift.plz,
        land: event.value.location.anschrift.land
      },
      lat: Number(event.value.location.lat),
      lon: Number(event.value.location.lon)
    },
    zeitmodell: {
      typ: event.value.zeitmodell.typ,
      datum: event.value.zeitmodell.datum,
      von: toIsoTime(event.value.zeitmodell.datum, event.value.zeitmodell.von),
      bis: toIsoTime(event.value.zeitmodell.datum, event.value.zeitmodell.bis),
      hinweis: event.value.zeitmodell.hinweis
    },
    eintritt: {
      kostenmodell: event.value.eintritt.kostenmodell,
      hinweis: event.value.eintritt.hinweis,
      tarife:
        event.value.eintritt.kostenmodell === "Kostenpflichtig"
          ? event.value.eintritt.tarife
          : []
    }
  }

  try {
    isSubmitting.value = true
    console.log("POST /activities payload:", payload)

    const response = await fetch("http://localhost:8000/activities", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json"
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error("Backend error:", errorText)
      throw new Error(errorText || "Failed to save event")
    }

    const result = await response.json()
    console.log("Event saved:", result)
    alert("Event erfolgreich hinzugefügt!")

    event.value = createEmptyEvent()
    selectedCategory.value = ""
  } catch (error) {
    console.error("Error adding event:", error)
    alert("Fehler beim Speichern des Events")
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.event-page {
  min-height: 100vh;
  padding: 48px 20px;
  background: #f4f7fb;
}

.event-shell {
  max-width: 860px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b;
}

.page-header h1 {
  margin: 0;
  font-size: 32px;
  line-height: 1.2;
  color: #0f172a;
}

.subtitle {
  margin: 12px 0 0;
  max-width: 680px;
  color: #475569;
  line-height: 1.6;
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 28px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eef2f7;
}

.form-section:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
}

.form-section h2 {
  margin: 0 0 2px;
  font-size: 18px;
  color: #0f172a;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.checkbox-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.checkbox-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid #dbe3ee;
  border-radius: 12px;
  background: #f8fafc;
  color: #334155;
}

.tarif-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border: 1px solid #dbe3ee;
  border-radius: 14px;
  background: #f8fafc;
}

input,
select,
textarea {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #dbe3ee;
  font-size: 14px;
  background: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease,
    background-color 0.2s ease;
  box-sizing: border-box;
  color: #0f172a;
}

textarea {
  min-height: 96px;
  resize: vertical;
}

input::placeholder,
textarea::placeholder {
  color: #94a3b8;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.14);
}

label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.button-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 4px;
}

button {
  padding: 13px 16px;
  border-radius: 12px;
  border: none;
  background: #2563eb;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s ease;
}

button:hover {
  background: #1d4ed8;
}

button:active {
  transform: scale(0.99);
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.secondary {
  background: #e2e8f0;
  color: #0f172a;
}

.secondary:hover {
  background: #cbd5e1;
}

@media (max-width: 700px) {
  .event-page {
    padding: 24px 14px;
  }

  .event-form {
    padding: 18px;
    border-radius: 16px;
  }

  .page-header h1 {
    font-size: 26px;
  }

  .grid-2,
  .button-row {
    grid-template-columns: 1fr;
  }
}
</style>