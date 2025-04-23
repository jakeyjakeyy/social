<script setup lang="ts">
import type { Notification } from '@/types/Notification';
import { onMounted, ref } from 'vue';

const props = defineProps<{
    notification: Notification;
}>();
const notification = props.notification;

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

const time = ref<string>(formatNotificationTime(notification.created_at));

const getNotificationMessage = (notification: Notification) => {
    switch (notification.action) {
        case "followed":
            return `${notification.action_account_displayname} followed you`;
        default:
            return `${notification.action_account_displayname} ${notification.action} your post.`;
    }
};

onMounted(() => {
    setInterval(() => {
        time.value = formatNotificationTime(notification.created_at);
    }, 1000); // Update every second
})
</script>

<template>
    <div class="notification-content">
        <p class="notification-message">
            {{ getNotificationMessage(notification) }}
        </p>
        <span class="notification-time">{{ time }}</span>
    </div>
</template>

<style scoped>
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
</style>