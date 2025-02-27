<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import Nav from "@/components/Nav.vue";
</script>

<template>
  <div class="social-media-container has-background">
    <Nav />
    <RouterView id="router-view" />
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

@media (max-width: 768px) {
  #router-view {
    margin-top: 3rem;
  }
}
</style>
