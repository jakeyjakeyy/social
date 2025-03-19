<script setup lang="ts">
import Post from "./Post.vue";
import type { Post as postType } from "@/types/Post";
const emit = defineEmits(["closeExpandedPost"]);
const props = defineProps<{ post: any }>();
import { onMounted, ref } from "vue";
import AddPost from "./AddPost.vue";

const postRef = ref<InstanceType<typeof Post> | null>(null);
const repliesRef = ref<HTMLDivElement | null>(null);
const showAddPost = ref(false);
let page = 1;

const replies = ref<postType[]>([]);

onMounted(() => {
  fetchReplies();
});

const clickBounds = (e: MouseEvent) => {
  if (!postRef.value || !repliesRef.value || showAddPost.value) return false;
  if (
    !postRef.value.$el.contains(e.target as Node) &&
    !repliesRef.value.contains(e.target as Node)
  ) {
    emit("closeExpandedPost");
  }
};

const fetchReplies = async () => {
  const res = await fetch(
    `${import.meta.env.VITE_BACKEND_URL}/api/post?page=${page}&replies=${
      props.post.id
    }`
  );
  const data = await res.json();
  replies.value = data;
};

const handleAddReply = (postId: number) => {
  showAddPost.value = true;
};

const handleCloseAddPost = (success: boolean) => {
  showAddPost.value = false;
  if (success) {
    fetchReplies();
  }
};
</script>
<template>
  <div class="expanded-post-overlay" @click="clickBounds">
    <div class="expanded-post-modal">
      <div class="expanded-post-content">
        <button class="close-button" @click="emit('closeExpandedPost')">
          <v-icon name="ri-close-line" scale="1.5" />
        </button>
        <div class="post-section">
          <Post
            :post="post"
            :expanded="true"
            ref="postRef"
            @add-reply="handleAddReply"
          />
        </div>
        <div class="replies-section">
          <div class="replies-header">
            <h3>Replies</h3>
            <span class="reply-count">{{ replies.length }}</span>
          </div>
          <div class="replies-container" ref="repliesRef">
            <div class="replies">
              <Post
                v-for="reply in replies"
                :key="reply.id"
                :post="reply"
                :expanded="false"
                @add-reply="handleAddReply"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    <AddPost
      v-if="showAddPost"
      :is-reply="post.id"
      @close-add-post-modal="handleCloseAddPost"
    />
  </div>
</template>

<style scoped>
.expanded-post-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(var(--background), 0.85);
  backdrop-filter: blur(12px);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.expanded-post-modal {
  width: 100%;
  max-width: 800px;
  margin: var(--spacing-lg) auto;
  background-color: var(--surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  position: relative;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

.expanded-post-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.close-button {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background-color: var(--surface-hover);
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  z-index: 1;
}

.close-button:hover {
  background-color: var(--surface-hover);
  transform: scale(1.1) rotate(90deg);
}

.post-section {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.replies-section {
  padding: var(--spacing-lg);
}

.replies-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.replies-header h3 {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.reply-count {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background-color: var(--surface-hover);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-full);
}

.replies-container {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
}

.replies {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  gap: var(--spacing-md);
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .expanded-post-overlay {
    padding: var(--spacing-sm);
  }

  .expanded-post-modal {
    margin: var(--spacing-sm) auto;
    border-radius: var(--radius-lg);
  }

  .expanded-post-content {
    gap: var(--spacing-md);
  }

  .post-section,
  .replies-section {
    padding: var(--spacing-md);
  }

  .close-button {
    top: var(--spacing-sm);
    right: var(--spacing-sm);
  }

  .replies-header {
    margin-bottom: var(--spacing-md);
  }
}
</style>
