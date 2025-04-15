<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from "vue";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import { useRouter } from "vue-router";

interface Notification {
  action: string;
  action_account: string;
  action_account_displayname: string;
  read: boolean;
  created_at: string;
  post_id: number | null;
  notification_id: number;
}

const serverURL = import.meta.env.VITE_BACKEND_URL;
const router = useRouter();
const notifications = ref<Notification[]>([]);
const unreadCount = ref(0);
const showDropdown = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);
const accountId = localStorage.getItem("account_id");
let token = getAccessToken();
let ws: WebSocket | null = null;
let notificationToken: string | null = null;
const page = ref(new Date().getTime());
const lastPage = ref(false);
const fetchingNotifications = ref(false);

const fetchNotificationToken = async () => {
  token = getAccessToken();
  const res = await fetch(`${serverURL}/api/notification/token`, {
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

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const handleScroll = () => {
  if (!dropdownRef.value) return;

  const { scrollTop, scrollHeight, clientHeight } = dropdownRef.value;
  if (scrollHeight - scrollTop - clientHeight < scrollHeight * 0.2) {
    getNotifications();
  }
};

const setupScrollListener = () => {
  if (dropdownRef.value) {
    dropdownRef.value.addEventListener("scroll", handleScroll);
  }
};

const cleanupScrollListener = () => {
  if (dropdownRef.value) {
    dropdownRef.value.removeEventListener("scroll", handleScroll);
  }
};

watch(showDropdown, (newValue) => {
  if (newValue) {
    nextTick(() => {
      setupScrollListener();
    });
  } else {
    cleanupScrollListener();
  }
});

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    showDropdown.value = false;
  }
};

const formatNotificationTime = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

const getNotificationMessage = (notification: Notification) => {
  switch (notification.action) {
    case "followed":
      return `${notification.action_account_displayname} followed you`;
    default:
      return `${notification.action_account_displayname} ${notification.action} your post.`;
  }
};

const callMarkAsRead = async (
  notification_id: number | null,
  type: string = "read"
) => {
  const res = await fetch(`${serverURL}/api/notification`, {
    method: "POST",

    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ notification_id, type }),
  });
  if (!res.ok) {
    try {
      const data = await RefreshToken();
      if (data.error) {
        console.log(data.message);
        return;
      }
      return await callMarkAsRead(notification_id);
    } catch (err) {
      console.log(err);
      return;
    }
  }
};

const markAsRead = async (index: number) => {
  let notification = notifications.value[index];
  if (!notification.read) {
    await callMarkAsRead(notification.notification_id);
    notifications.value[index].read = true;
    if (unreadCount.value > 0) {
      unreadCount.value--;
    }
  }

  // Handle navigation based on notification type
  if (notification.post_id) {
    router.push(`/post/${notification.post_id}`);
  } else {
    router.push(`/@${notification.action_account}`);
  }
};

const initWebSocket = async () => {
  notificationToken = await fetchNotificationToken();
  const protocol = serverURL.startsWith("https") ? "wss" : "ws";
  const stripURL = serverURL.replace("http://", "").replace("https://", "");
  ws = new WebSocket(
    `${protocol}://${stripURL}/ws/notification/${accountId}/?token=${notificationToken}`
  );
  if (!ws) {
    console.log("WebSocket connection failed");
    return;
  }

  ws.onmessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    if (data.type === "delete_notification") {
      const notification = notifications.value.find(
        (notification) => notification.notification_id === data.id
      );
      if (notification) {
        notifications.value = notifications.value.filter(
          (notification) => notification.notification_id !== data.id
        );
        if (!notification.read) {
          unreadCount.value--;
        }
      }
    } else {
      const notification = data.message;
      notifications.value.unshift(notification);
      if (!notification.read) {
        unreadCount.value++;
      }
    }
  };
  ws.onclose = async () => {
    await initWebSocket();
  };
};

const getNotifications = async () => {
  if (lastPage.value || fetchingNotifications.value) return;
  fetchingNotifications.value = true;
  const res = await fetch(
    `${serverURL}/api/notification?timestamp=${page.value}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  const data = await res.json();
  notifications.value.push(...data);
  unreadCount.value = notifications.value.filter(
    (notification) => !notification.read
  ).length;
  if (data.length === 0) {
    lastPage.value = true;
  } else {
    page.value = new Date(
      notifications.value[notifications.value.length - 1].created_at
    ).getTime();
  }
  fetchingNotifications.value = false;
};

const markAllAsRead = async () => {
  await callMarkAsRead(null, "all");
  notifications.value.forEach((notification) => {
    notification.read = true;
  });
  unreadCount.value = 0;
};

onMounted(async () => {
  await getNotifications();
  await initWebSocket();
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
  if (ws) {
    ws.close();
  }
});
</script>

<template>
  <div class="notification-container">
    <div class="notification-icon" @click.stop="toggleDropdown">
      <v-icon name="ri-notification-3-line" />
      <span v-if="unreadCount > 0" class="notification-badge">{{
        unreadCount
      }}</span>
    </div>

    <div v-if="showDropdown" class="notification-dropdown" ref="dropdownRef" @click.stop>
      <div class="notification-header">
        <div class="notification-header-content">
          <h3>Notifications</h3>
          <button v-if="unreadCount > 0" @click="markAllAsRead" class="mark-all-as-read-button">
            <v-icon name="ri-check-line" />
          </button>
        </div>
      </div>
      <div class="notification-list">
        <div v-if="notifications.length === 0" class="notification-empty">
          No notifications yet
        </div>
        <div v-for="(notification, index) in notifications" :key="index" class="notification-item"
          :class="{ unread: !notification.read }" @click="markAsRead(index)">
          <div class="notification-content">
            <p class="notification-message">
              {{ getNotificationMessage(notification) }}
            </p>
            <span class="notification-time">{{
              formatNotificationTime(notification.created_at)
            }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notification-container {
  position: relative;
}

.notification-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  cursor: pointer;
  color: var(--text-primary);
  padding: 8px;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background-color: var(--danger);
  color: white;
  font-size: var(--font-size-xs);
  font-weight: 600;
  border-radius: var(--radius-full);
}

.notification-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: -90px;
  width: 300px;
  max-height: 400px;
  overflow-y: auto;
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
}

.notification-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--surface-hover);
  position: sticky;
  top: 0;
  background-color: var(--surface);
  z-index: 1;
}

.notification-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.notification-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mark-all-as-read-button {
  font-size: var(--font-size-sm);
  color: var(--primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
}

.mark-all-as-read-button:hover {
  background-color: var(--surface-hover);
}

.notification-list {
  padding: var(--spacing-xs);
}

.notification-item {
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
  cursor: pointer;
  margin-bottom: 4px;
}

.notification-item:hover {
  background-color: var(--surface-hover);
}

.notification-item.unread {
  background-color: rgba(37, 99, 235, 0.05);
}

.notification-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.notification-message {
  margin: 0;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  line-height: 1.4;
}

.notification-time {
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
}

.notification-empty {
  padding: var(--spacing-md);
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .notification-dropdown {
    position: fixed;
    top: 96px;
    left: 0;
    right: 0;
    width: 100%;
    max-height: calc(100vh - 96px);
    border-radius: 0;
    border-top: 1px solid var(--surface-hover);
  }

  .notification-icon {
    padding: 6px;
  }

  .notification-badge {
    min-width: 16px;
    height: 16px;
    font-size: 10px;
  }

  .notification-header {
    padding: var(--spacing-sm);
  }

  .notification-header h3 {
    font-size: var(--font-size-md);
  }

  .notification-item {
    padding: var(--spacing-sm);
  }

  .notification-message {
    font-size: var(--font-size-sm);
  }
}
</style>
