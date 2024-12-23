<script setup lang="ts">
import { onMounted, ref } from "vue";
import Post from "./Post.vue";
import { useRoute } from "vue-router";
import type { Post as posttype } from "@/types/Post";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
let page = 1;
const route = useRoute();
const username = route.params.username as string;
const posts = ref<posttype[]>([]);

const fetchPosts = async () => {
  const res = await fetch(`${BACKEND_URL}/api/profile/${username}/${page}`);
  const data = await res.json();
  posts.value = data;
};

onMounted(async () => {
  await fetchPosts();
});
</script>
<template>
  <div>
    <h1>Profile of @{{ username }}</h1>
    <Post v-for="post in posts" :key="post.id" :post="post" />
  </div>
</template>

<style scoped></style>
