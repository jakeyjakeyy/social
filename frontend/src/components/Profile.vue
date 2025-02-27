<script setup lang="ts">
import { onMounted, ref } from "vue";
import Post from "./Post.vue";
import { useRoute } from "vue-router";
import type { Post as posttype } from "@/types/Post";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
let access_token = getAccessToken();
let page = 1;
const route = useRoute();
const username = route.params.username as string;
const posts = ref<posttype[]>([]);

const fetchPosts = async () => {
  const res = await fetch(`${BACKEND_URL}/api/profile/${username}/${page}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(access_token && { Authorization: `Bearer ${access_token}` }),
    },
  });
  const data = await res.json();
  if (data.detail) {
    let refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      access_token = getAccessToken();
      await fetchPosts();
    }
    return;
  }
  posts.value = data;
};

onMounted(async () => {
  await fetchPosts();
});
</script>
<template>
  <div class="profile-container">
    <h1>Profile of @{{ username }}</h1>
    <Post
      v-if="posts.length"
      v-for="post in posts"
      :key="post.id"
      :post="post"
      :expanded="false"
    />
    <div v-else class="skeleton-container">
      <div v-for="i in 16" class="skeleton-block"></div>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
  overflow: auto;
  scrollbar-width: thin;
}

.skeleton-container {
  display: flex;
  width: 100%;
  flex-direction: column;
  justify-content: start;
  align-items: start;
  padding-top: 2rem;
}

.skeleton-block {
  width: 50%;
}
</style>
