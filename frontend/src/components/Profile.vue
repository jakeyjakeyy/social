<script setup lang="ts">
import { useRoute } from "vue-router";

const route = useRoute();
const username = route.params.username as string;
</script>
<template>
  <div>
    <h1>Profile of @{{ username }}</h1>
  </div>
</template>

<style scoped></style>
