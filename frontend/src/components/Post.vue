<script setup lang="ts">
import router from "@/router";
import type { Post } from "@/types/Post";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import { MdPreview } from "md-editor-v3";
import "md-editor-v3/lib/preview.css";
import { onBeforeUnmount, onMounted, ref } from "vue";
import ExpandedPost from "./ExpandedPost.vue";
import { sanitizeHTML } from "@/utils/SanitizeHTML";

type Themes = "light" | "dark";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const props = defineProps<{ post: Post; expanded: boolean }>();
const emit = defineEmits(["deletePost"]);
let post = props.post;
let repostData: Post | null = null;
const isRepost = ref(post.is_repost);
const expanded = props.expanded;
const contentContainer = ref<HTMLDivElement | null>(null);
const isContentTruncated = ref(false);
const isExpanded = ref(false);
const showExpandedPost = ref(false);
const theme = ref<Themes>("dark");

if (post.is_repost && post.original_post) {
  repostData = post;
  post = post.original_post;
}

const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (
      mutation.type === "attributes" &&
      mutation.attributeName === "data-theme"
    ) {
      const newTheme = (mutation.target as HTMLElement).getAttribute(
        "data-theme"
      );
      theme.value =
        newTheme === "light" || newTheme === "dark" ? newTheme : "dark";
    }
  });
});

onMounted(() => {
  theme.value =
    <Themes>document.getElementById("app-body")?.getAttribute("data-theme") ||
    "dark";
  observer.observe(document.getElementById("app-body")!, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
});
onBeforeUnmount(() => {
  observer.disconnect();
});

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
    const refresh = await RefreshToken();
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

const deletePost = async (id: number) => {
  const access_token = getAccessToken();
  const res = await fetch(`${BACKEND_URL}/api/post?id=${id}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${access_token}`,
    },
  });
  const data = await res.json();
  if (data.detail) {
    const refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      await deletePost(id);
    }
  } else {
    await router.push("/");
  }
  emit("deletePost", id);
};

const toggleShowExpandedPost = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  const isFooterClick = target.closest(".card-footer");
  const isMedia = target.closest(".media");
  const isExpandedClick = target.closest(".expanded-post");

  if (!isMedia && !isFooterClick && !isExpandedClick && !expanded) {
    showExpandedPost.value = !showExpandedPost.value;
  }
};
</script>

<template>
  <div class="post card" @click="toggleShowExpandedPost">
    <div class="reply-to" v-if="post.reply_to">
      <v-icon name="fa-grip-lines-vertical" />
    </div>
    <div v-if="isRepost && repostData" class="reposted-by">
      <p>
        <v-icon name="ri-repeat-2-line" />
        <span>Reposted by {{ repostData.account_display_name }}</span>
      </p>
    </div>
    <div v-if="post.type === 'image'" class="card-image">
      <figure class="image is-4by3">
        <img :src="`${BACKEND_URL}/api${post.url}`" alt="Post Image" />
      </figure>
    </div>
    <div class="card-content">
      <div class="media" @click="router.push(`/@${post.account_username}`)">
        <div class="media-left">
          <figure class="image is-48x48">
            <!-- <img
                :src="`${BACKEND_URL}/api${post.account_avatar}`"
                alt="User Avatar"
              /> -->
            <img
              src="https://bulma.io/assets/images/placeholders/96x96.png"
              alt="Placeholder image"
            />
          </figure>
        </div>
        <div class="media-content">
          <p class="title is-4">{{ post.account_display_name }}</p>
          <p class="subtitle is-6">@{{ post.account_username }}</p>
        </div>
      </div>
      <div v-if="post.type === 'markdown'" class="markdown-post">
        <MdPreview
          id="post.id"
          :model-value="post.content"
          :theme="theme"
          language="en-US"
          :sanitize="sanitizeHTML"
        />
      </div>
    </div>
    <div class="content has-text-weight-semibold">
      {{ post.type === "text" || post.type === "image" ? post.content : "" }}
      <br />
      <time class="has-text-weight-light is-size-7">{{
        new Date(post.created_at).toLocaleString()
      }}</time>
    </div>
    <footer class="card-footer">
      <div class="card-footer-item">
        <v-icon name="bi-chat-left" />
        <!-- <span>{{ post.reply_count }}</span> -->
      </div>
      <div class="favorites card-footer-item" @click="submitAction('favorite')">
        <span>{{ post.favorite_count }}</span>
        <span>
          <v-icon v-if="!post.favorited" name="bi-heart" />
          <v-icon v-else name="bi-heart-fill" class="has-text-danger" />
        </span>
      </div>
      <div class="reposts card-footer-item" @click="submitAction('repost')">
        <span>{{ post.repost_count }}</span>
        <span>
          <v-icon v-if="!post.reposted" name="ri-repeat-2-line" />
          <v-icon v-else name="ri-repeat-2-fill" class="has-text-success" />
        </span>
      </div>
      <div
        v-if="post.is_owner"
        class="card-footer-item"
        @click="deletePost(post.id)"
      >
        <v-icon name="fa-regular-trash-alt" class="has-text-danger" />
      </div>
    </footer>
    <ExpandedPost
      v-if="showExpandedPost"
      :post="post.reply_to ? post.reply_to : post"
      @close="showExpandedPost = false"
      @close-expanded-post="showExpandedPost = false"
    />
  </div>
</template>

<style scoped>
.post {
  width: 50%;
}

.media {
  cursor: pointer;
  width: fit-content;
  padding-right: 1rem;
}

.card-footer-item {
  gap: 1rem;
  cursor: pointer;
}

.reply-to {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.markdown-post {
  max-height: 50vh;
  overflow: auto;
}

@media (max-width: 768px) {
  .post {
    width: 90%;
    margin: 0.5rem 0;
  }
}
</style>
