<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import Nav from "@/components/Nav.vue";
</script>

<template>
  <div class="app-container">
    <Nav />
    <main class="main-content">
      <RouterView id="router-view" />
    </main>
  </div>
</template>

<style>
@import "@/assets/styles/design-system.css";

#app {
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--background);
  color: var(--text-primary);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.grid {
  display: grid;
  gap: var(--spacing-md);
}

.grid-cols-1 {
  grid-template-columns: repeat(1, 1fr);
}
.grid-cols-2 {
  grid-template-columns: repeat(2, 1fr);
}
.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}
.grid-cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 1024px) {
  .grid-cols-4 {
    grid-template-columns: repeat(3, 1fr);
  }

  .main-content {
    padding: var(--spacing-sm);
  }
}

@media (max-width: 768px) {
  .grid-cols-3 {
    grid-template-columns: repeat(2, 1fr);
  }

  .container {
    padding: 0 var(--spacing-sm);
  }
}

@media (max-width: 640px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, 1fr);
  }

  .main-content {
    padding: var(--spacing-xs);
  }
}

@media (min-width: 641px) {
  .main-content {
    padding-top: var(--spacing-lg);
  }
}
</style>
