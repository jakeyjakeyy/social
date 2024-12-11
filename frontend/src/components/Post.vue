<script setup lang="ts">
import type { Post } from "@/types/Post";
const props = defineProps<{ post: Post }>();
const post = props.post;
</script>

<template>
  <div class="post">
    <p>{{ post.content }}</p>
    <p>
      {{ post.account_display_name }}
      <span class="account-link has-text-primary"
        >@{{ post.account_username }}</span
      >
    </p>
  </div>
</template>

<style scoped>
.post {
  display: flex;
  flex-direction: column;
  text-align: left;
  border: 1px solid #ccc;
  padding: 1rem;
  margin: 1rem;
  width: 50%;
}

.account-link {
  cursor: pointer;
}
</style>
