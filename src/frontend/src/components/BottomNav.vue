<template>
  <div class="bottom-nav">
    <button
      class="focus-btn"
      type="button"
      @click="$emit('focus')"
      aria-label="Focus own location"
      title="Focus"
    >
    <span class="material-icons">
      gps_fixed
    </span>
    </button>

    <button class="nav-item" :class="{ active: activeTab === 'favourites' }" @click="$emit('tab', 'favourites')">
      <span class="nav-ic">
        <span class="material-icons">
        favorite
        </span>
      </span>
      <span>Favourites</span>
    </button>

    <button class="nav-item" :class="{ active: activeTab === 'home' }" @click="$emit('tab', 'home')">
      <span class="nav-ic">
        <span class="material-icons icon">home</span>
      </span>
      <span>Home</span>
    </button>

    <button class="nav-item" :class="{ active: activeTab === 'settings' }" @click="$emit('tab', 'settings')">
      <span class="nav-ic">
        <span class="material-icons">
        person
        </span>
      </span>
      <span>My Profile</span>
    </button>
      <button v-if="canAdd" class="nav-item" :class="{ active: activeTab === 'add-event' }" @click="$emit('tab', 'add-event')">
        <span class="nav-ic">
          <span class="material-icons">
          add_circle
          </span>
        </span>
        <span>Add Event</span>
      </button>
  </div>
</template>

<script setup lang="ts">
  defineProps<{ activeTab: "home" | "favourites" | "settings" | "add-event"; canAdd?: boolean }>()

defineEmits<{
  (e: "tab", t: "home" | "favourites" | "settings" | "add-event"): void
  (e: "focus"): void
}>()
</script>

<style scoped>
.bottom-nav {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: var(--nav-bottom);
  z-index: 1000;

  width: min(520px, calc(100vw - 35px));
  height: var(--nav-h);

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;

  border-radius: 22px;

  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(17, 24, 39, 0.08);
  box-shadow:
    0 22px 60px rgba(0, 0, 0, 0.18),
    0 1px 0 rgba(255, 255, 255, 0.6) inset;

  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.bottom-nav::before {
  content: "";
  position: absolute;
  left: 14px;
  right: 14px;
  top: 10px;
  height: 1px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.55);
  pointer-events: none;
}

.focus-btn {
  width: 42px;
  min-width: 42px;
  height: 42px;
  border: none;
  border-radius: 999px;
  background: rgba(47, 91, 255, 0.1);
  color: #0b4dff;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
}

.focus-btn:hover {
  background: rgba(47, 91, 255, 0.16);
}

.focus-btn:active {
  transform: scale(0.97);
}

.focus-dot {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: #2f5bff;
  border: 3px solid #ffffff;
  box-shadow: 0 0 0 2px rgba(47, 91, 255, 0.18);
}

.nav-item {
  flex: 1;
  height: 52px;
  border: none;
  background: transparent;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;

  border-radius: 16px;

  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;

  color: rgba(17, 24, 39, 0.55);

  position: relative;
  cursor: pointer;
  user-select: none;

  transition:
    transform 160ms ease,
    background 160ms ease,
    color 160ms ease,
    box-shadow 160ms ease;
}

.icon-img {
  width: 32px;
  height: 32px;
}

.nav-item .nav-ic {
  font-size: 18px;
  line-height: 1;
  transform: translateY(1px);
  transition: transform 160ms ease, filter 160ms ease;
}

.nav-item:hover {
  background: rgba(17, 24, 39, 0.04);
  color: rgba(17, 24, 39, 0.75);
}

.nav-item:active {
  transform: scale(0.98);
}

.nav-item.active {
  color: #0b4dff;
  background: rgba(47, 91, 255, 0.12);
}

.nav-item.active .nav-ic {
  transform: translateY(0px) scale(1.02);
  filter: saturate(1.1);
}

@media (min-width: 900px) {
  .bottom-nav {
    width: min(1108px, calc(100vw - 40px));
    height: var(--nav-h);
    padding: 8px 10px;
    border-radius: 18px;

    background: rgba(255, 255, 255, 0.82);
    box-shadow:
      0 18px 50px rgba(0, 0, 0, 0.16),
      0 1px 0 rgba(255, 255, 255, 0.65) inset;
  }

  .focus-btn {
    width: 44px;
    min-width: 44px;
    height: 44px;
  }

  .nav-item {
    flex-direction: row;
    gap: 10px;

    height: calc(var(--nav-h) - 16px);
    border-radius: 14px;

    font-size: 12px;
    padding: 0 14px;
    justify-content: center;
  }

  .nav-item.active {
    background: rgba(47, 91, 255, 0.10);
  }

  .nav-item .nav-ic {
    font-size: 18px;
    transform: none;
  }
}
</style>