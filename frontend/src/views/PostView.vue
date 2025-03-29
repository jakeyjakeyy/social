<script setup lang="ts">
import ExpandedPost from "@/components/ExpandedPost.vue";
import type { Post as PostType } from "@/types/Post";
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { getAccessToken } from "@/utils/RefreshToken";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const route = useRoute();
const postId = route.params.id;
const post = ref<PostType | null>(null);
async function getPost() {
  const token = getAccessToken();
  const res = await fetch(`${BACKEND_URL}/api/post?id=${postId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  const data = await res.json();
  post.value = data;
}

onMounted(() => {
  getPost();
});
</script>

<template>
  <ExpandedPost v-if="post" :post="post" not-modal />
</template>

<style scoped></style>
