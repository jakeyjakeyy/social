<script setup lang="ts">
import { onMounted, ref } from "vue";
import Post from "./Post.vue";
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
    <div class="content container">
      <Post v-for="post in posts" :key="post.id" :post="post" />
    </div>
  </div>
</template>

<style scoped>
.home-container,
.content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
