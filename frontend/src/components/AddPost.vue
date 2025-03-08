<script lang="ts" setup>
import {onMounted, ref} from "vue";
import {getAccessToken, RefreshToken} from "@/utils/RefreshToken";
import {MdEditor} from "md-editor-v3";
import "md-editor-v3/lib/style.css";

type Themes = "light" | "dark";

const props = defineProps<{ isReply: boolean | number }>();
const emit = defineEmits(["closeAddPostModal"]);
const MAX_POST_LEN = 255;
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const content = ref("");
const access_token = getAccessToken();
const type = ref("text");
let image: File | null = null;
const theme = ref<Themes>("dark");

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

const submitPost = async () => {
  let data;
  let status;
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
        ...(props.isReply && {reply_id: props.isReply}),
      }),
    });
    data = await res.json();
    status = res.status;
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
    status = res.status;
  }
  if (data.detail) {
    const refresh = await RefreshToken();
    if (refresh.error) {
      alert("Please login again");
    } else {
      await submitPost();
    }
  } else if (status !== 200) {
    alert(data.message);
  } else {
    emit("closeAddPostModal", true); // true to toggle success notification
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

const setImage = (e: Event) => (image = (e.target as HTMLInputElement).files?.[0] || null);
</script>

<template>
  <div class="modal is-active">
    <div class="modal-background"></div>
    <div class="modal-content">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">Add Post</p>
          <button
            aria-label="close is-large"
            class="delete"
            @click="emit('closeAddPostModal')"
          ></button>
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
              <label class="label has-text-current">Content</label>
              <div class="control">
                <textarea
                  v-model="content"
                  :maxlength="MAX_POST_LEN"
                  class="textarea"
                  placeholder="Content"
                  style="resize: none; overflow: auto"
                ></textarea>
                <div class="help">
                  {{ content.length }} / {{ MAX_POST_LEN }}
                </div>
              </div>
            </div>
            <div v-else-if="type == 'markdown'" class="field">
              <label class="label has-text-current">Content</label>
              <div class="control">
                <MdEditor v-model="content" :theme="theme" language="en-US"/>
              </div>
            </div>
            <div v-else-if="type == 'image'" class="field">
              <label class="label has-text-current">Image</label>
              <div class="control">
                <input
                  class="input"
                  type="file"
                  @change="(e) => setImage(e)"
                />
              </div>
              <label class="label has-text-current">Caption</label>
              <div class="control">
                <textarea
                  v-model="content"
                  :maxlength="MAX_POST_LEN"
                  class="textarea"
                  placeholder="Caption"
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

.selector {
  display: flex;
  justify-content: space-around;
  margin: 0 1rem;
}

.delete {
  cursor: pointer;
  margin: 0.5rem;
}
</style>
