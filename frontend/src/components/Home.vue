<script lang="ts" setup>
import {onMounted, ref} from "vue";
import Post from "./Post.vue";
import {getAccessToken, RefreshToken} from "@/utils/RefreshToken"
import type {Post as PostType} from "@/types/Post";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const posts = ref<PostType[]>([]);
let access_token = getAccessToken();
let page = 1;
const lastPage = ref<boolean>(false);
let scrollPosition = 0;
let fetchingPosts = false;
const allButtonRef = ref<HTMLButtonElement | null>(null);
const followingButtonRef = ref<HTMLButtonElement | null>(null);

onMounted(async () => {
  await fetchPosts();
  const homePosts: HTMLElement | null = document.getElementById("home-posts");
  if (homePosts) {
    homePosts.addEventListener("scroll", async () => {
      if (
        homePosts.scrollTop + homePosts.clientHeight >=
        homePosts.scrollHeight * 0.75 &&
        !lastPage.value &&
        homePosts.scrollTop > scrollPosition &&
        !fetchingPosts
      ) {
        scrollPosition = homePosts.scrollTop;
        page++;
        const oldPosts = posts.value;
        fetchingPosts = true;
        await fetchPosts();
        if (oldPosts.length === posts.value.length) {
          page--;
          lastPage.value = true;
        }
        fetchingPosts = false;
      }
    });
  }
});
const fetchPosts = async (followingFeed = false) => {
  let path;
  if (followingFeed) {
    path = `${BACKEND_URL}/api/post?page=${page}&following=true`;
  } else {
    path = `${BACKEND_URL}/api/post?page=${page}`;
  }
  const res = await fetch(`${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(access_token && {Authorization: `Bearer ${access_token}`}),
    },
  });
  const data = await res.json();

  if (data.detail) {
    const refresh = await RefreshToken();
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

const toggleFeed = async (e: MouseEvent) => {
  page = 1;
  posts.value = [];
  if (e.target === allButtonRef.value) {
    allButtonRef.value?.classList.add("is-primary");
    followingButtonRef.value?.classList.remove("is-primary");
    await fetchPosts();
  } else {
    followingButtonRef.value?.classList.add("is-primary");
    allButtonRef.value?.classList.remove("is-primary");
    await fetchPosts(true);
  }
};
</script>

<template>
  <div class="home-container">
    <div class="content-selections">
      <button ref="allButtonRef" class="button is-primary" @click="toggleFeed">
        All
      </button>
      <button ref="followingButtonRef" class="button" @click="toggleFeed">
        Following
      </button>
    </div>
    <div id="home-posts" class="content">
      <div class="posts-wrapper" v-if="posts.length">
        <Post
          v-for="post in posts"
          :key="post.id"
          :expanded="false"
          :post="post"
          @delete-post="fetchPosts"
        />
      </div>
      <div v-else class="skeleton-container">
        <div v-for="i in 16" :key="i" class="skeleton-block"></div>
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
.skeleton-container,
.posts-wrapper {
  display: flex;
  width: 100%;
  flex-direction: column;
  justify-content: start;
  align-items: center;
}

.content {
  height: 100vh;
  padding-bottom: 25vh;
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
