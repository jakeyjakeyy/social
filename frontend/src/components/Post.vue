<script setup lang="ts">
import router from "@/router";
import type { Post } from "@/types/Post";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const props = defineProps<{ post: Post }>();
const post = props.post;

const submitAction = async (action: string) => {
  const access_token = getAccessToken();
  const res = await fetch(`${BACKEND_URL}/api/post`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify({
      type: action,
      post_id: post.id,
    }),
  });
  const data = await res.json();
  if (data.detail) {
    let refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      await submitAction(action);
    }
  } else {
    if (action === "favorite") {
      post.favorited = !post.favorited;
      post.favorite_count = post.favorited
        ? post.favorite_count + 1
        : post.favorite_count - 1;
    } else if (action === "repost") {
      post.reposted = !post.reposted;
      post.repost_count = post.reposted
        ? post.repost_count + 1
        : post.repost_count - 1;
    }
  }
};
</script>

<template>
  <div class="post card">
    <p v-if="post.type === 'text'">{{ post.content }}</p>
    <div class="card-footer">
      <p>
        {{ post.account_display_name }}
        <span
          class="account-link has-text-primary"
          @click="router.push(`/@${post.account_username}`)"
          >@{{ post.account_username }}</span
        >
      </p>
      <div class="post-controls">
        <div class="favorites">
          <span>{{ post.favorite_count }}</span>
          <button
            class="button is-small is-primary"
            @click="submitAction('favorite')"
          >
            {{ post.favorited ? "Unfavorite" : "Favorite" }}
          </button>
        </div>
        <div class="reposts">
          <span>{{ post.repost_count }}</span>
          <button
            class="button is-small is-info"
            @click="submitAction('repost')"
          >
            {{ post.reposted ? "Unrepost" : "Repost" }}
          </button>
        </div>
      </div>
    </div>
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

.post-controls {
  display: flex;
  justify-content: space-between;
  margin-left: 1rem;
  gap: 1rem;
}
</style>
