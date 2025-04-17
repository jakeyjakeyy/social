<script setup lang="ts">
import router from "@/router";
import type { Post } from "@/types/Post";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import { MdPreview } from "md-editor-v3";
import "md-editor-v3/lib/preview.css";
import { onBeforeUnmount, onMounted, ref } from "vue";
import ExpandedPost from "./ExpandedPost.vue";
import { sanitizeHTML } from "@/utils/SanitizeHTML";
import AddPost from "./AddPost.vue";
import { Teleport } from "vue";

type Themes = "light" | "dark";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const props = defineProps<{
  post: Post;
  expanded?: boolean;
  isReply?: boolean;
}>();
const emit = defineEmits(["deletePost", "expandPost", "addReply"]);
let post = props.post;
let repostData: Post | null = null;
const isRepost = ref(post.is_repost);
const expanded = props.expanded;
const showExpandedPost = ref(false);
const theme = ref<Themes>("dark");
const showAddPost = ref(false);
const showReplyTo = ref(false);
const isReply = props.isReply;
const showNotification = ref(false);

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

const deletePost = async (id: number, emitOnly?: boolean) => {
  if (!emitOnly) {
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
  }
  emit("deletePost", id);
};

const toggleShowExpandedPost = (e: MouseEvent | KeyboardEvent) => {
  const target = e.target as HTMLElement;
  const isFooterClick = target.closest(".card-footer");
  const isMedia = target.closest(".media");
  const isExpandedClick = target.closest(".expanded-post");
  const isReplyClick = target.closest(".reply-to");

  if (!isMedia && !isFooterClick && !isExpandedClick && !showAddPost.value) {
    if (!expanded) {
      showExpandedPost.value = true;
    }
    if (isReplyClick) {
      showExpandedPost.value = true;
      showReplyTo.value = true;
    }
  }
};

const handleCloseExpandedPost = () => {
  showExpandedPost.value = false;
  showReplyTo.value = false;
};

const handleCloseAddPost = (success: boolean) => {
  showAddPost.value = false;
  if (success) {
    emit("deletePost", post.id);
  }
};

const copyLink = () => {
  navigator.clipboard.writeText(`${window.location.origin}/post/${post.id}`);
  showNotification.value = true;
  setTimeout(() => {
    showNotification.value = false;
  }, 3000);
};
</script>

<template>
  <div class="post card" @click="toggleShowExpandedPost" @keydown.enter="toggleShowExpandedPost" tabindex="0">
    <button class="reply-to" v-if="post.reply_to && !isReply" aria-label="View Original Post">
      <v-icon name="fa-grip-lines-vertical" />
    </button>
    <div v-if="isRepost && repostData" class="reposted-by">
      <p>
        <v-icon name="ri-repeat-2-line" />
        <span>Reposted by {{ repostData.account_display_name }}</span>
      </p>
    </div>
    <div v-if="post.type === 'image'" class="card-image">
      <figure class="image is-4by3">
        <img :src="`${BACKEND_URL}/api${post.url}`" alt="Post Image" class="post-image" />
      </figure>
    </div>
    <div class="card-content">
      <button class="media" @click="router.push(`/@${post.account_username}`)">
        <div class="media-left">
          <figure class="image is-48x48">
            <img :src="post.account_profile_picture
              ? `${BACKEND_URL}/api${post.account_profile_picture}`
              : 'https://bulma.io/assets/images/placeholders/96x96.png'
              " alt="User Avatar" />
            <figcaption>
              User Avatar
            </figcaption>
          </figure>
        </div>
        <div class="media-content">
          <p class="title is-4">{{ post.account_display_name }}</p>
          <p class="subtitle is-6">@{{ post.account_username }}</p>
        </div>
      </button>
      <div v-if="post.type === 'markdown'" class="markdown-post">
        <MdPreview id="post.id" :model-value="post.content" :theme="theme" language="en-US" :sanitize="sanitizeHTML" />
      </div>
      <div class="content has-text-weight-semibold">
        {{ post.type === "text" || post.type === "image" ? post.content : "" }}
        <br />
        <time class="has-text-weight-light is-size-7">{{
          new Date(post.created_at).toLocaleString()
          }}</time>
      </div>
    </div>
    <footer class="card-footer">
      <button class="card-footer-item" @click.stop="showAddPost = true" aria-label="Reply">
        <v-icon name="bi-chat-left" />
        <span>{{ post.reply_count }}</span>
      </button>
      <button class="favorites card-footer-item" @click="submitAction('favorite')" aria-label="Favorite">
        <span>{{ post.favorite_count }}</span>
        <span>
          <v-icon v-if="!post.favorited" name="bi-heart" />
          <v-icon v-else name="bi-heart-fill" class="has-text-danger" />
        </span>
      </button>
      <button class="reposts card-footer-item" @click="submitAction('repost')" aria-label="Repost">
        <span>{{ post.repost_count }}</span>
        <span>
          <v-icon v-if="!post.reposted" name="ri-repeat-2-line" />
          <v-icon v-else name="ri-repeat-2-fill" class="has-text-success" />
        </span>
      </button>
      <button class="card-footer-item" @click="copyLink" aria-label="Copy Link">
        <v-icon name="ri-share-line" />
      </button>
      <button v-if="post.is_owner" class="card-footer-item" @click="deletePost(post.id)" aria-label="Delete Post">
        <v-icon name="fa-regular-trash-alt" class="has-text-danger" />
      </button>
    </footer>
  </div>

  <Teleport to="body">
    <ExpandedPost v-if="showExpandedPost" :post="showReplyTo ? post.reply_to : post"
      @close-expanded-post="handleCloseExpandedPost" @delete-post="deletePost(post.id, true)" />
    <AddPost v-if="showAddPost" :is-reply="post.id" @close-add-post-modal="handleCloseAddPost" />
    <div v-if="showNotification" class="notification">
      Link copied to clipboard
    </div>
  </Teleport>
</template>

<style scoped>
.post {
  width: 100%;
  max-width: 600px;
  margin: var(--spacing-md) auto;
  transition: transform var(--transition-fast),
    box-shadow var(--transition-fast);
  border: 1px solid var(--border-color);
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.post:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary);
}

.media {
  cursor: pointer;
  width: fit-content;
  padding-right: var(--spacing-md);
  transition: opacity var(--transition-fast);
}

.media:hover {
  opacity: 0.8;
}

.media-left {
  border-radius: var(--radius-full);
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-around;
  padding: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background-color: var(--surface-hover);
}

.card-footer-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.card-footer-item:hover {
  background-color: var(--surface);
  color: var(--primary);
}

.reply-to {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding: var(--spacing-sm);
  color: var(--info);
  border-bottom: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.reply-to:hover {
  color: var(--primary);
  cursor: pointer;
  background-color: var(--info);
  border-radius: var(--radius-md);
  box-shadow: 0 2px 5px rgba(var(--primary-rgb), 0.1);
}

.reply-to:hover::after {
  content: "View original post";
  position: absolute;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
  opacity: 0.8;
  animation: fadeIn 0.3s ease-in-out;
}

.reply-to svg {
  transition: transform var(--transition-fast), color var(--transition-fast);
}

.reply-to:hover svg {
  transform: scale(0);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 0.8;
  }
}

.reposted-by {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  border-bottom: 1px solid var(--border-color);
}

.post-image {
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  object-fit: cover;
  border-bottom: 1px solid var(--border-color);
}

.markdown-post {
  max-height: 50vh;
  overflow: auto;
  box-shadow: 0 0 15px -2px var(--primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin: var(--spacing-md) 0;
  border: 1px solid var(--border-color);
}

.card-content {
  padding: var(--spacing-lg);
}

.notification {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  text-align: center;
  background-color: var(--surface);
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-md);
  animation: slideUp 0.3s ease-in, slideDown 0.3s ease-out 2.8s;
  z-index: 999;
  transform-origin: bottom;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes slideDown {
  from {
    transform: translateY(0);
    opacity: 1;
  }

  to {
    transform: translateY(100%);
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .post {
    width: 100%;
    margin: var(--spacing-sm) 0;
    border-radius: var(--radius-md);
  }
}
</style>
