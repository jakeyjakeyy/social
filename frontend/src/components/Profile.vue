<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import Post from "./Post.vue";
import { useRoute } from "vue-router";
import type { Post as posttype } from "@/types/Post";
import { checkToken, getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import type { ProfileInfo } from "@/types/ProfileInfo";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
let access_token = getAccessToken();
let page = 1;
const route = useRoute();
let username = route.params.username as string;
const posts = ref<posttype[]>([]);
const isFollowing = ref<boolean>(false);
const profileInfo = ref<ProfileInfo | null>(null);
const loggedIn = checkToken();
const isOwner = ref<boolean>(false);

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

const checkFollow = async () => {
  const res = await fetch(`${BACKEND_URL}/api/follow?username=${username}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(access_token && { Authorization: `Bearer ${access_token}` }),
    },
  });
  const data = await res.json();
  if (res.status != 200) {
    alert(data.message);
  }
  if (data.detail) {
    let refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      access_token = getAccessToken();
      await checkFollow();
    }
    return;
  }
  isFollowing.value = data.following;
};
const handleFollow = async () => {
  const res = await fetch(`${BACKEND_URL}/api/follow`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(access_token && { Authorization: `Bearer ${access_token}` }),
    },
    body: JSON.stringify({ username }),
  });
  let data = await res.json();
  if (res.status != 200) {
    alert(data.message);
  }
  if (data.detail) {
    let refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      access_token = getAccessToken();
      await handleFollow();
    }
  }
  if (res.status == 400) {
    alert(data.detail);
  }
  isFollowing.value = !isFollowing.value;
};

const fetchProfileInfo = async () => {
  const res = await fetch(
    `${BACKEND_URL}/api/profile/info?username=${username}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...(access_token && { Authorization: `Bearer ${access_token}` }),
      },
    }
  );
  const data = await res.json();
  if (data.detail) {
    let refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      access_token = getAccessToken();
      await fetchProfileInfo();
    }
  }
  profileInfo.value = data;
  isOwner.value = data.is_owner;
};

const loadProfileData = async () => {
  posts.value = [];
  page = 1;
  username = route.params.username as string;
  await fetchProfileInfo();
  await fetchPosts();
  if (loggedIn) await checkFollow();
};

onMounted(async () => {
  await loadProfileData();
});

watch(
  () => route.params.username,
  (newUsername) => {
    if (newUsername) {
      loadProfileData();
    }
  }
);
</script>
<template>
  <div class="profile-container">
    <div class="card profile-header">
      <div class="card-image">
        <figure class="image banner-image">
          <img
            src="https://bulma.io/assets/images/placeholders/1280x960.png"
            alt="Placeholder image"
          />
          <div v-if="isOwner" class="image-overlay">
            <span class="icon">
              <v-icon name="bi-camera" color="white" />
            </span>
          </div>
        </figure>
      </div>
      <div class="card-content">
        <div class="media">
          <div class="media-left">
            <figure class="image is-128x128 profile-image-container">
              <img
                src="https://bulma.io/assets/images/placeholders/128x128.png"
                alt="Placeholder image"
              />
              <div v-if="isOwner" class="image-overlay">
                <span class="icon">
                  <v-icon name="bi-camera" color="white" />
                </span>
              </div>
            </figure>
          </div>
          <div class="media-content">
            <p v-if="profileInfo" class="title is-3">
              {{ profileInfo.display_name }}
            </p>
            <p class="title is-3">@{{ username }}</p>
          </div>
          <div v-if="!isOwner && loggedIn" class="follow-container">
            <button class="button" @click="handleFollow">
              {{ isFollowing ? "Unfollow" : "Follow" }}
            </button>
          </div>
        </div>
      </div>
      <footer class="card-footer">
        <p class="card-footer-item">
          <span class="has-text-weight-bold">{{ profileInfo?.followers }}</span>
          <p>Followers</p>
        </p>
        <p class="card-footer-item">
          <span class="has-text-weight-bold">{{ profileInfo?.following }}</span>
          <p>Following</p>
        </p>
      </footer>
    </div>
    <div v-if="posts.length" class="posts">
      <Post
        v-for="post in posts"
        :key="post.id"
        :post="post"
        :expanded="false"
      />
    </div>
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
  justify-content: center;
  align-items: center;
  padding-top: 2rem;
}

.skeleton-block {
  width: 50%;
}

.profile-header {
  width: 100%;
}

.banner-image img {
  width: 100%;
  height: 25vh;
  object-fit: cover;
}

.posts {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.card-footer-item {
  gap: 1rem;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
}

.banner-image:hover .image-overlay,
.profile-image-container:hover .image-overlay {
  opacity: 1;
}

</style>
