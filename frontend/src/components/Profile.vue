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
const username = ref(route.params.username as string);
const posts = ref<posttype[]>([]);
const expandedPost = ref<posttype | null>(null);
const isFollowing = ref<boolean>(false);
const profileInfo = ref<ProfileInfo | null>(null);
const loggedIn = checkToken();
const isOwner = ref<boolean>(false);
const profileFileInput = ref<HTMLInputElement | null>(null);
const bannerFileInput = ref<HTMLInputElement | null>(null);
const lastPage = ref<boolean>(false);
let scrollPosition = 0;
let fetchingPosts = false;

const fetchPosts = async () => {
  const res = await fetch(
    `${BACKEND_URL}/api/profile/${username.value}/${page}`,
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
      await fetchPosts();
    }
    return;
  }
  posts.value = [...posts.value, ...data];
};

const handleFollow = async () => {
  const res = await fetch(`${BACKEND_URL}/api/follow`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(access_token && { Authorization: `Bearer ${access_token}` }),
    },
    body: JSON.stringify({ username: username.value }),
  });
  let data = await res.json();
  if (res.status != 200) {
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
    `${BACKEND_URL}/api/profile/info?username=${username.value}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...(access_token && { Authorization: `Bearer ${access_token}` }),
      },
    }
  );
  const data = await res.json();
  if (res.status != 200) {
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
  isFollowing.value = data.is_following;
};

const loadProfileData = async () => {
  posts.value = [];
  page = 1;
  username.value = route.params.username as string;
  await fetchProfileInfo();
  await fetchPosts();
};

onMounted(async () => {
  await loadProfileData();

  // Infinite scroll
  window.addEventListener("scroll", async () => {
    if (
      window.scrollY + window.innerHeight >=
        document.documentElement.scrollHeight * 0.75 &&
      !lastPage.value &&
      window.scrollY > scrollPosition &&
      !fetchingPosts
    ) {
      scrollPosition = window.scrollY;
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
});

watch(
  () => route.params.username,
  (newUsername) => {
    if (newUsername) {
      loadProfileData();
    }
  }
);

const uploadPhoto = async (type: string) => {
  if (type === "pfp") {
    profileFileInput.value?.click();
  } else if (type === "banner") {
    bannerFileInput.value?.click();
  }
};

const handleFileUpload = async (event: Event, type: string) => {
  const input = event.target as HTMLInputElement;
  if (!input.files || input.files.length === 0) return;

  const file = input.files[0];
  const formData = new FormData();
  formData.append("username", username.value);
  formData.append("file", file);
  formData.append("type", type);

  try {
    const res = await fetch(`${BACKEND_URL}/api/profile/info`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
      body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
      if (data.detail) {
        let refresh = await RefreshToken();
        if (refresh.error) {
          alert("Please login again");
        } else {
          access_token = getAccessToken();
          await handleFileUpload(event, type);
        }
        return;
      }
      alert(data.message || "Failed to upload image");
    } else {
      await fetchProfileInfo();
    }
  } catch (error) {
    console.error("Error uploading image:", error);
    alert("Failed to upload image");
  }

  input.value = "";
};
</script>
<template>
  <div class="profile-container">
    <div class="card profile-header">
      <div class="card-image">
        <figure class="image banner-image">
          <img
            :src="
              profileInfo?.banner_picture
                ? `${BACKEND_URL}/api${profileInfo.banner_picture}`
                : 'https://bulma.io/assets/images/placeholders/1280x960.png'
            "
            alt="Banner image"
          />
          <div
            v-if="isOwner"
            class="image-overlay"
            @click="uploadPhoto('banner')"
          >
            <span class="icon">
              <v-icon name="bi-camera" color="white" />
            </span>
            <input
              type="file"
              ref="bannerFileInput"
              @change="($event) => handleFileUpload($event, 'banner')"
              style="display: none"
              accept="image/*"
            />
          </div>
        </figure>
      </div>
      <div class="card-content">
        <div class="media">
          <div class="media-left">
            <figure class="image is-128x128 profile-image-container">
              <img
                :src="
                  profileInfo?.profile_picture
                    ? `${BACKEND_URL}/api${profileInfo.profile_picture}`
                    : 'https://bulma.io/assets/images/placeholders/128x128.png'
                "
                alt="Profile Picture"
                class="avatar"
              />
              <div
                v-if="isOwner"
                class="image-overlay"
                @click="uploadPhoto('pfp')"
              >
                <span class="icon">
                  <v-icon name="bi-camera" color="white" />
                </span>
                <input
                  type="file"
                  ref="profileFileInput"
                  @change="($event) => handleFileUpload($event, 'pfp')"
                  style="display: none"
                  accept="image/*"
                />
              </div>
            </figure>
          </div>
          <div class="media-content">
            <p v-if="profileInfo" class="title is-3">
              {{ profileInfo.display_name }}
            </p>
            <p class="subtitle is-5">@{{ username }}</p>
          </div>
          <div v-if="!isOwner && loggedIn" class="follow-container">
            <button
              class="button"
              :class="{ 'is-primary': isFollowing }"
              @click="handleFollow"
            >
              {{ isFollowing ? "Following" : "Follow" }}
            </button>
          </div>
        </div>
      </div>
      <footer class="card-footer">
        <div class="card-footer-item">
          <span class="has-text-weight-bold">{{ profileInfo?.followers }}</span>
          <p class="subtitle is-6">Followers</p>
        </div>
        <div class="card-footer-item">
          <span class="has-text-weight-bold">{{ profileInfo?.following }}</span>
          <p class="subtitle is-6">Following</p>
        </div>
      </footer>
    </div>
    <div v-if="posts.length" class="posts">
      <Post v-for="post in posts" :key="post.id" :post="post" />
    </div>
    <div v-if="lastPage" class="end-of-posts">
      <p>You've reached the end</p>
    </div>
    <div v-else class="skeleton-container">
      <div class="skeleton-block"></div>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-md);
  gap: var(--spacing-lg);
}

.profile-header {
  width: 100%;
  overflow: hidden;
}

.banner-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.banner-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  padding: var(--spacing-lg);
}

.media {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-lg);
}

.media-left {
  margin-top: -64px;
}

.profile-image-container {
  position: relative;
  border-radius: var(--radius-full);
  border: 4px solid var(--surface);
  box-shadow: var(--shadow-md);
  background-color: var(--surface);
  overflow: hidden;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-full);
}

.media-content {
  flex: 1;
}

.title {
  margin-bottom: var(--spacing-xs);
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
}

.follow-container {
  margin-left: auto;
}

.button {
  min-width: 100px;
  transition: all var(--transition-fast);
}

.button.is-primary {
  background-color: var(--primary);
  color: white;
}

.button.is-primary:hover {
  background-color: var(--primary-hover);
}

.card-footer {
  display: flex;
  justify-content: space-around;
  padding: var(--spacing-lg);
  border-top: 1px solid var(--surface-hover);
}

.card-footer-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.card-footer-item span {
  font-size: var(--font-size-xl);
  color: var(--text-primary);
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
  transition: opacity var(--transition-fast);
  cursor: pointer;
}

.banner-image:hover .image-overlay,
.profile-image-container:hover .image-overlay {
  opacity: 1;
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

.posts {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  width: 100%;
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
  .profile-container {
    padding: var(--spacing-sm);
  }

  .media {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .media-left {
    margin-top: -48px;
  }

  .follow-container {
    margin: var(--spacing-md) 0 0;
  }

  .banner-image {
    height: 150px;
  }
}
</style>
