<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";

const notifications = ref<string[]>([]);
const accountId = localStorage.getItem("account_id");
const token = getAccessToken();

const fetchNotificationToken = async () => {
  const res = await fetch("http://localhost:8000/api/notification/token", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    try {
      const data = await RefreshToken();
      if (data.error) {
        console.log(data.message);
        return null;
      }
      return await fetchNotificationToken();
    } catch (err) {
      console.log(err);
      return null;
    }
  }
  const data = await res.json();
  return data.token;
};

onMounted(async () => {
  const notificationToken = await fetchNotificationToken();

  const ws = new WebSocket(
    `ws://localhost:8000/ws/notification/${accountId}/?token=${notificationToken}`
  );
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
