<script setup lang="ts">
import { onMounted, ref } from "vue";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const posts: any = ref([]);

onMounted(async () => {
  posts.value = await fetchPosts();
  console.log(posts.value);
});
const fetchPosts = async () => {
  const res = await fetch(`${BACKEND_URL}/api/post/1`);
  const data = await res.json();
  return data;
};
</script>

<template>
  <div class="home-container">
    <div class="content">
      <div v-for="post in posts" :key="post.id">
        <p>{{ post.content }}</p>
        <p>
          {{ post.account_display_name }}
          <span>@{{ post.account_username }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
