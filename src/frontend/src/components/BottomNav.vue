<template>
  <div class="bottom-nav">
    <button class="nav-item" :class="{ active: activeTab === 'favourites' }" @click="$emit('tab', 'favourites')">
      <span class="nav-ic">
        <img src="/icons/bookmark_heart.svg" alt="Favourites" class="icon-img" />
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
      <span class="nav-ic">⚙️</span>
      <span>Settings</span>
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ activeTab: "home" | "favourites" | "settings" }>()
defineEmits<{ (e: "tab", t: "home" | "favourites" | "settings"): void }>()
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
  box-shadow: 0 10px 28px rgba(47, 91, 255, 0.22);
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
    box-shadow: 0 8px 20px rgba(47, 91, 255, 0.18);
  }

  .nav-item .nav-ic {
    font-size: 18px;
    transform: none;
  }
}
</style>