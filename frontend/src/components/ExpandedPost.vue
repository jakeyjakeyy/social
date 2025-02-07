<script setup lang="ts">
import Post from "./Post.vue";
const emit = defineEmits(["closeExpandedPost"]);
const props = defineProps<{ post: any }>();
import { ref } from "vue";

const postRef = ref<InstanceType<typeof Post> | null>(null);
const repliesRef = ref<HTMLDivElement | null>(null);

const clickBounds = (e: MouseEvent) => {
  if (!postRef.value || !repliesRef.value) return false;
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
    <div class="post-replies" ref="repliesRef">replies go here</div>
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
