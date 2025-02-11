<script setup lang="ts">
import Post from "./Post.vue";
const emit = defineEmits(["closeExpandedPost"]);
const props = defineProps<{ post: any }>();
import { ref } from "vue";
import AddPost from "./AddPost.vue";

const postRef = ref<InstanceType<typeof Post> | null>(null);
const repliesRef = ref<HTMLDivElement | null>(null);
const showAddPost = ref(false);

const clickBounds = (e: MouseEvent) => {
  if (!postRef.value || !repliesRef.value || showAddPost.value) return false;
  if (
    !postRef.value.$el.contains(e.target as Node) &&
    !repliesRef.value.contains(e.target as Node)
  ) {
    emit("closeExpandedPost");
  }
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
      <div class="replies">replies go here</div>
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
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 10;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
