<script setup lang="ts">
import { onMounted, ref } from "vue";
let root: HTMLElement = document.getElementById("app-body") as HTMLElement;
let themeLight = ref(root.getAttribute("data-theme") === "light");

const toggleTheme = () => {
  themeLight.value = !themeLight.value;
  if (root && themeLight.value) {
    root.setAttribute("data-theme", "light");
  } else if (root) {
    root.setAttribute("data-theme", "dark");
  }
};

onMounted(() => {
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
  <div class="theme-selector has-text-info">
    <v-icon
      id="theme-icon"
      :name="themeLight ? 'fa-moon' : 'fa-sun'"
      scale="1"
      @click="toggleTheme"
    />
  </div>
</template>

<style scoped>
.theme-selector {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

#theme-icon {
  cursor: pointer;
}
</style>
