<script setup lang="ts">
import { onMounted, ref } from "vue";
const emit = defineEmits(["toggleTheme"]);
let root: HTMLElement = document.getElementById("app-body") as HTMLElement;
let themeLight = ref(root.getAttribute("data-theme") === "light");
let userTheme = localStorage.getItem("theme");

const toggleTheme = () => {
  themeLight.value = !themeLight.value;
  if (root && themeLight.value) {
    root.setAttribute("data-theme", "light");
    localStorage.setItem("theme", "light");
  } else if (root) {
    root.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
  }
  emit("toggleTheme");
};

onMounted(() => {
  if (userTheme) {
    themeLight.value = userTheme === "light";
    root.setAttribute("data-theme", userTheme);
    return;
  }
  const localTheme = root.getAttribute("data-theme");
  if (localTheme === "light") {
    themeLight.value = true;
    root.setAttribute("data-theme", "light");
  } else if (localTheme === "dark") {
    themeLight.value = false;
    root.setAttribute("data-theme", "dark");
  }
});
</script>

<template>
  <div class="theme-selector">
    <button
      class="theme-button"
      @click="toggleTheme"
      :title="themeLight ? 'Switch to dark mode' : 'Switch to light mode'"
    >
      <v-icon :name="themeLight ? 'fa-moon' : 'fa-sun'" scale="1.2" />
    </button>
  </div>
</template>

<style scoped>
.theme-selector {
  display: flex;
  justify-content: center;
  align-items: center;
}

.theme-button {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-button:hover {
  background-color: var(--surface-hover);
  color: var(--text-primary);
  transform: scale(1.1);
}

.theme-button:active {
  transform: scale(0.95);
}

@media (max-width: 768px) {
  .theme-selector {
    margin-left: 10px;
  }
}
</style>
