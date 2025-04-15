<script lang="ts" setup>
import { onMounted, ref } from "vue";
import Post from "./Post.vue";
import ExpandedPost from "./ExpandedPost.vue";
import { checkToken, getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import type { Post as PostType } from "@/types/Post";
import AddPost from "./AddPost.vue";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const posts = ref<PostType[]>([]);
const expandedPost = ref<PostType | null>(null);
const showAddPost = ref(false);
const replyToPostId = ref<number | null>(null);
let access_token = getAccessToken();
let page = new Date().getTime();
const lastPage = ref<boolean>(false);
let scrollPosition = 0;
let fetchingPosts = false;
const allButtonRef = ref<HTMLButtonElement | null>(null);
const followingButtonRef = ref<HTMLButtonElement | null>(null);
const loggedIn = ref<boolean>(checkToken());
const followingFeed = ref<boolean>(false);

onMounted(async () => {
  await fetchPosts();
  window.addEventListener("scroll", async () => {
    if (
      window.scrollY + window.innerHeight >=
      document.documentElement.scrollHeight * 0.75 &&
      !lastPage.value &&
      window.scrollY > scrollPosition &&
      !fetchingPosts
    ) {
      scrollPosition = window.scrollY;
      page = new Date(posts.value[posts.value.length - 1].created_at).getTime();
      const oldPosts = posts.value;
      fetchingPosts = true;
      await fetchPosts();
      if (oldPosts.length === posts.value.length) {
        lastPage.value = true;
      }
      fetchingPosts = false;
    }
  });
});

const fetchPosts = async (followingFeed = false) => {
  let path;
  if (followingFeed) {
    path = `${BACKEND_URL}/api/post?timestamp=${page}&following=true`;
  } else {
    path = `${BACKEND_URL}/api/post?timestamp=${page}`;
  }
  const res = await fetch(`${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(access_token && { Authorization: `Bearer ${access_token}` }),
    },
  });
  const data = await res.json();

  if (res.status != 200) {
    const refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      access_token = getAccessToken();
      return await fetchPosts();
    }
    return;
  }

  posts.value = [...posts.value, ...data];
};

const toggleFeed = async (e: MouseEvent) => {
  page = new Date().getTime();
  posts.value = [];
  if (e.target === allButtonRef.value) {
    followingFeed.value = false;
    allButtonRef.value?.classList.add("is-primary");
    followingButtonRef.value?.classList.remove("is-primary");
    await fetchPosts();
  } else {
    followingFeed.value = true;
    followingButtonRef.value?.classList.add("is-primary");
    allButtonRef.value?.classList.remove("is-primary");
    await fetchPosts(true);
  }
};

const handleAddReply = (postId: number) => {
  replyToPostId.value = postId;
  showAddPost.value = true;
};

const handleCloseAddPost = (success: boolean) => {
  showAddPost.value = false;
  if (success) {
    fetchPosts();
  }
};
</script>

<template>
  <div class="home-container">
    <div v-if="loggedIn" class="content-selections">
      <button ref="allButtonRef" class="button" :class="{ 'is-primary': !followingFeed }" @click="toggleFeed">
        All Posts
      </button>
      <button ref="followingButtonRef" class="button" :class="{ 'is-primary': followingFeed }" @click="toggleFeed">
        Following
      </button>
    </div>
    <div id="home-posts" class="content">
      <div class="posts-wrapper" v-if="posts.length">
        <Post v-for="post in posts" :key="post.id" :post="post" @delete-post="fetchPosts" />
      </div>
      <div v-else class="skeleton-container">
        <div class="skeleton-block"></div>
      </div>
      <div v-if="lastPage" class="end-of-posts">
        <p>You've reached the end</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-md);
  gap: var(--spacing-lg);
}

.content-selections {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  width: 100%;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--surface-hover);
}

.button {
  flex: 1;
  max-width: 200px;
  transition: all var(--transition-fast);
}

.content {
  width: 100%;
  min-height: calc(100vh - 200px);
  overflow-y: auto;
  scrollbar-width: thin;
}

.posts-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  width: 100%;
}

.skeleton-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  width: 100%;
}

.skeleton-block {
  height: 200px;
  background: var(--surface);
  border-radius: var(--radius-lg);
  animation: pulse 2s infinite;
}

.end-of-posts {
  text-align: center;
  padding: var(--spacing-xl) 0;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }

  50% {
    opacity: 0.8;
  }

  100% {
    opacity: 0.6;
  }
}

@media (max-width: 768px) {
  .home-container {
    padding: var(--spacing-sm);
  }

  .content-selections {
    padding: var(--spacing-sm) 0;
  }

  .button {
    max-width: none;
  }
}
</style>
