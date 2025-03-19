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

/* Modern Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--surface);
}

::-webkit-scrollbar-thumb {
  background: var(--surface-hover);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Modern Selection */
::selection {
  background-color: var(--primary);
  color: white;
}

/* Modern Focus Styles */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* Modern Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Modern Container */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

/* Modern Grid System */
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

/* Responsive Breakpoints */
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

/* Mobile-first adjustments */
@media (min-width: 641px) {
  .main-content {
    padding-top: var(--spacing-lg);
  }
}
</style>
