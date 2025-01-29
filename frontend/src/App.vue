<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import Nav from "@/components/Nav.vue";
</script>

<template>
  <div class="social-media-container">
    <Nav />
    <RouterView />
  </div>
</template>

<style scoped>
.social-media-container {
  display: flex;
  flex-direction: row;
  height: 100vh;
  overflow: hidden;
  align-items: start;
}
</style>
