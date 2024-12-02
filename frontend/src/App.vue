<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import Nav from "@/components/Nav.vue";
</script>

<template>
  <div class="social-media-container container">
    <RouterView />
    <Nav />
  </div>
</template>

<style scoped>
/* .social-media-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
} */
</style>
