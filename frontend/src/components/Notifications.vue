<script setup lang="ts">
import { ref, onMounted } from "vue";

const notifications = ref<string[]>([]);
const accountId = localStorage.getItem("account_id");

onMounted(() => {
  const ws = new WebSocket(`ws://localhost:8000/ws/notification/${accountId}/`);
  ws.onmessage = (event: MessageEvent) => {
    notifications.value.push(event.data);
    console.log(notifications.value);
  };
});
</script>

<template>
  <div>Notifications</div>
</template>

<style scoped></style>
