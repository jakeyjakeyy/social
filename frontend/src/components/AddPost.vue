<script setup lang="ts">
import { ref } from "vue";
import { getAccessToken } from "@/utils/RefreshToken";
const emit = defineEmits(["closeAddPostModal"]);
const MAX_POST_LEN = 255;
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const content = ref("");
const access_token = getAccessToken();

const submitPost = async () => {
  const res = await fetch(`${BACKEND_URL}/api/post`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${access_token}`,
    },
    body: JSON.stringify({ content: content.value, type: "text" }),
  });
  emit("closeAddPostModal");
};
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-content">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">Add Post</p>
        </header>

        <div class="card-content">
          <form @submit.prevent>
            <div class="field">
              <label class="label">Content</label>
              <div class="control">
                <textarea
                  class="textarea"
                  placeholder="Content"
                  v-model="content"
                  :maxlength="MAX_POST_LEN"
                  style="resize: none; overflow: auto"
                ></textarea>
                <div class="help">
                  {{ content.length }} / {{ MAX_POST_LEN }}
                </div>
              </div>
            </div>
            <div class="field">
              <div class="control">
                <button
                  class="button is-primary is-fullwidth"
                  @click="submitPost"
                >
                  Add Post
                </button>
              </div>
            </div>
          </form>
          <button
            class="modal-close is-large"
            aria-label="close"
            @click="emit('closeAddPostModal')"
          ></button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-content {
  padding: 20px;
  margin: 20px;
}

.modal-close {
  position: absolute;
  top: 0;
  right: 0;
  margin: 0.5rem;
}
</style>
