<script setup lang="ts">
import { onMounted, ref } from "vue";
import Post from "./Post.vue";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const posts: any = ref([]);
let access_token = getAccessToken();
let page = 1;
const lastPage: any = ref(false);

onMounted(async () => {
  await fetchPosts();
  const homePosts: any = document.getElementById("home-posts");
  homePosts.addEventListener("scroll", async () => {
    if (
      homePosts.scrollTop + homePosts.clientHeight >= homePosts.scrollHeight &&
      !lastPage.value
    ) {
      page++;
      const oldPosts = posts.value;
      await fetchPosts();
      if (oldPosts.length === posts.value.length) {
        page--;
        lastPage.value = true;
      }
    }
  });
});
const fetchPosts = async () => {
  const res = await fetch(`${BACKEND_URL}/api/post?page=${page}`, {
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

  posts.value = [...posts.value, ...data];
};
</script>

<template>
  <div class="home-container">
    <div class="content" id="home-posts">
      <Post
        v-if="posts.length"
        v-for="post in posts"
        :key="post.id"
        :post="post"
        @delete-post="fetchPosts"
        :expanded="false"
      />
      <div v-else class="skeleton-container">
        <div v-for="i in 16" class="skeleton-block"></div>
      </div>
      <div v-if="lastPage" class="end-of-posts">
        <p>End of posts</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container,
.content,
.skeleton-container {
  display: flex;
  width: 100%;
  flex-direction: column;
  justify-content: start;
  align-items: start;
}
.content {
  height: 100vh;
  overflow-y: auto;
  scrollbar-width: thin;
}

.skeleton-container {
  padding-top: 2rem;
}

.skeleton-block {
  width: 50%;
}

/* @media (max-width: 768px) {
  .content {
    margin-top: 3rem;
  }
} */
</style>
