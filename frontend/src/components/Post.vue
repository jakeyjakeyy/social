<script setup lang="ts">
import router from "@/router";
import type { Post } from "@/types/Post";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import { MdPreview } from "md-editor-v3";
import "md-editor-v3/lib/preview.css";
import { onBeforeUnmount, onMounted, ref } from "vue";
import ExpandedPost from "./ExpandedPost.vue";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const props = defineProps<{ post: Post; expanded: boolean }>();
const emit = defineEmits(["deletePost"]);
const post = props.post;
const expanded = props.expanded;
const contentContainer = ref<HTMLDivElement | null>(null);
const isContentTruncated = ref(false);
const isExpanded = ref(false);
const showExpandedPost = ref(false);

onMounted(() => {
  checkContentHeight();
  window.addEventListener("resize", checkContentHeight);
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", checkContentHeight);
});

function checkContentHeight() {
  if (contentContainer.value) {
    isContentTruncated.value =
      contentContainer.value.scrollHeight > window.innerHeight / 4;
  }
}

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

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
  contentContainer.value!.style.maxHeight = isExpanded.value ? "none" : "25vh";
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
    let refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      await deletePost(id);
    }
  } else {
    router.push("/");
  }
  emit("deletePost", id);
};

const toggleShowExpandedPost = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  const isControlsClick = target.closest(".post-controls");
  const isOwnerClick = target.closest(".post-owner");
  const isExpandedClick = target.closest(".expanded-post");

  if (!isOwnerClick && !isControlsClick && !isExpandedClick && !expanded) {
    showExpandedPost.value = !showExpandedPost.value;
  }
};
</script>

<template>
  <div class="post card" @click="toggleShowExpandedPost">
    <div class="content" ref="contentContainer">
      <p v-if="post.type === 'text'">{{ post.content }}</p>
      <div v-else-if="post.type === 'markdown'" class="markdown-post">
        <MdPreview
          id="post.id"
          :model-value="post.content"
          theme="dark"
          language="en-US"
        />
      </div>
      <div v-else-if="post.type === 'image'" class="image-post">
        <p>{{ post.content }}</p>
        <img :src="`${BACKEND_URL}/api${post.url}`" alt="Post Image" />
      </div>
    </div>
    <div class="card-footer">
      <div class="post-owner">
        <p>
          {{ post.account_display_name }}
          <span
            class="account-link has-text-primary"
            @click="router.push(`/@${post.account_username}`)"
            >@{{ post.account_username }}</span
          >
        </p>
        <button
          v-if="post.is_owner"
          class="button is-small is-danger"
          @click="deletePost(post.id)"
        >
          Delete
        </button>
      </div>
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
        <div v-if="isContentTruncated" class="expand">
          <button class="button is-small" @click="toggleExpand">
            {{ isExpanded ? "Collapse" : "Expand" }}
          </button>
        </div>
      </div>
    </div>
    <ExpandedPost
      v-if="showExpandedPost"
      :post="post"
      @close="showExpandedPost = false"
      @close-expanded-post="showExpandedPost = false"
    />
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

.card-footer {
  display: flex;
  justify-content: space-between;
  cursor: pointer;
}

.content {
  max-height: 25vh;
  overflow: auto;
  margin: 0;
  cursor: pointer;
}

.image-post {
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
