<script setup lang="ts">
import { ref } from "vue";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import { MdEditor } from "md-editor-v3";
import "md-editor-v3/lib/style.css";

const props = defineProps<{ isReply: boolean | number }>();
const emit = defineEmits(["closeAddPostModal"]);
const MAX_POST_LEN = 255;
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const content = ref("");
const access_token = getAccessToken();
const type = ref("text");
let image: File | null = null;

const submitPost = async () => {
  let data;
  if (type.value != "image") {
    const res = await fetch(`${BACKEND_URL}/api/post`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${access_token}`,
      },
      body: JSON.stringify({
        content: content.value,
        type: type.value,
        ...(props.isReply && { reply_id: props.isReply }),
      }),
    });
    data = await res.json();
  } else if (image) {
    const formData = new FormData();
    formData.append("type", "image");
    formData.append("image", image);
    formData.append("caption", content.value);
    const res = await fetch(`${BACKEND_URL}/api/post`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
      body: formData,
    });
    data = await res.json();
  }
  if (data.detail) {
    let refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      await submitPost();
    }
  } else {
    emit("closeAddPostModal", true); // true to toggle sucess notification
  }
};

const toggleType = (newType: string) => {
  type.value = newType;
  const textButton = document.getElementById("toggleTextButton");
  const blogButton = document.getElementById("toggleBlogButton");
  const imageButton = document.getElementById("toggleImageButton");
  if (!textButton || !blogButton || !imageButton) return;
  if (newType === "text") {
    textButton.classList.add("is-active");
    blogButton.classList.remove("is-active");
    imageButton.classList.remove("is-active");
  } else if (newType === "markdown") {
    textButton.classList.remove("is-active");
    blogButton.classList.add("is-active");
    imageButton.classList.remove("is-active");
  } else if (newType === "image") {
    textButton.classList.remove("is-active");
    blogButton.classList.remove("is-active");
    imageButton.classList.add("is-active");
  }
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

        <div class="selector">
          <div
            id="toggleTextButton"
            class="button is-active"
            @click="toggleType('text')"
          >
            Text Post
          </div>
          <div
            id="toggleBlogButton"
            class="button"
            @click="toggleType('markdown')"
          >
            Blog Post
          </div>
          <div
            id="toggleImageButton"
            class="button"
            @click="toggleType('image')"
          >
            Image Post
          </div>
        </div>

        <div class="card-content">
          <form @submit.prevent>
            <div v-if="type == 'text'" class="field">
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
            <div v-else-if="type == 'markdown'" class="field">
              <label class="label">Content</label>
              <div class="control">
                <MdEditor v-model="content" theme="dark" language="en-US" />
              </div>
            </div>
            <div v-else-if="type == 'image'" class="field">
              <label class="label">Image</label>
              <div class="control">
                <input
                  type="file"
                  class="input"
                  @change="(e:any) => (image = e.target.files[0])"
                />
              </div>
              <label class="label">Caption</label>
              <div class="control">
                <textarea
                  class="textarea"
                  placeholder="Caption"
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

.selector {
  display: flex;
  justify-content: space-around;
  margin: 0 1rem;
}

.selector-item {
  cursor: pointer;
}
</style>
