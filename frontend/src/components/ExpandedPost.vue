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
</script>
<template>
  <div class="expanded-post" @click="clickBounds">
    <Post :post="post" :expanded="true" ref="postRef" />

    <div class="replies-container" ref="repliesRef">
      <button @click="showAddPost = !showAddPost" class="button">
        Add Reply
      </button>
      <AddPost
        v-if="showAddPost"
        ref="addPostRef"
        @close-add-post-modal="showAddPost = false"
        :is-reply="post.id"
      />
      <div class="replies">
        <Post
          v-for="reply in replies"
          :key="reply.id"
          :post="reply"
          :expanded="false"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.expanded-post {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  max-height: 100vh;
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 10;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  overflow: auto;
}

.replies-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 50%;
}

.replies {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
}

@media (max-width: 768px) {
  .replies-container {
    width: 75%;
  }
}
</style>
