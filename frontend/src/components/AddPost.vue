<script lang="ts" setup>
import { onMounted, ref } from "vue";
import { getAccessToken, RefreshToken } from "@/utils/RefreshToken";
import { MdEditor } from "md-editor-v3";
import "md-editor-v3/lib/style.css";
import { sanitizeHTML } from "@/utils/SanitizeHTML";

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
        ...(props.isReply && { reply_id: props.isReply }),
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

const setImage = (e: Event) =>
  (image = (e.target as HTMLInputElement).files?.[0] || null);
</script>

<template>
  <div class="modal is-active add-post-modal">
    <div class="modal-background"></div>
    <div class="modal-content">
      <div class="card add-post-card">
        <header class="card-header">
          <p class="card-header-title">
            {{ isReply ? "Reply" : "Create Post" }}
          </p>
          <button
            aria-label="close"
            class="delete"
            @click="emit('closeAddPostModal')"
          ></button>
        </header>

        <div class="post-type-selector">
          <div
            id="toggleTextButton"
            class="button"
            :class="{ 'is-primary': type === 'text' }"
            @click="toggleType('text')"
          >
            <v-icon name="ri-text" />
            <span>Text</span>
          </div>
          <div
            id="toggleBlogButton"
            class="button"
            :class="{ 'is-primary': type === 'markdown' }"
            @click="toggleType('markdown')"
          >
            <v-icon name="ri-markdown-line" />
            <span>Blog</span>
          </div>
          <div
            id="toggleImageButton"
            class="button"
            :class="{ 'is-primary': type === 'image' }"
            @click="toggleType('image')"
          >
            <v-icon name="ri-image-line" />
            <span>Image</span>
          </div>
        </div>

        <div class="card-content">
          <form @submit.prevent>
            <div v-if="type === 'text'" class="field">
              <label class="label">Content</label>
              <div class="control">
                <textarea
                  v-model="content"
                  :maxlength="MAX_POST_LEN"
                  class="textarea"
                  placeholder="What's on your mind?"
                  style="resize: none; overflow: auto"
                ></textarea>
                <div class="help">
                  {{ content.length }} / {{ MAX_POST_LEN }}
                </div>
              </div>
            </div>
            <div v-else-if="type === 'markdown'" class="field">
              <label class="label">Content</label>
              <div class="control">
                <MdEditor
                  v-model="content"
                  :theme="theme"
                  language="en-US"
                  :sanitize="sanitizeHTML"
                />
              </div>
            </div>
            <div v-else-if="type === 'image'" class="field">
              <label class="label">Image</label>
              <div class="control">
                <div class="file-input-wrapper">
                  <input
                    class="file-input"
                    type="file"
                    @change="(e) => setImage(e)"
                    accept="image/*"
                  />
                  <div class="file-input-label">
                    <v-icon name="ri-upload-cloud-line" />
                    <span>Choose an image</span>
                  </div>
                </div>
                <div v-if="image" class="selected-file">
                  <span>{{ image.name }}</span>
                  <button
                    class="delete is-small"
                    @click="image = null"
                  ></button>
                </div>
              </div>
              <div class="field">
                <label class="label">Caption</label>
                <div class="control">
                  <textarea
                    v-model="content"
                    :maxlength="MAX_POST_LEN"
                    class="textarea"
                    placeholder="Add a caption to your image"
                    style="resize: none; overflow: auto"
                  ></textarea>
                  <div class="help">
                    {{ content.length }} / {{ MAX_POST_LEN }}
                  </div>
                </div>
              </div>
            </div>
            <div class="field">
              <div class="control">
                <button
                  class="button is-primary is-fullwidth"
                  @click="submitPost"
                >
                  {{ isReply ? "Reply" : "Post" }}
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
.modal {
  z-index: 1000;
}
.modal-content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--spacing-md);
  margin: var(--spacing-md);
  width: 100%;
  height: 100%;
}

.add-post-card {
  width: 100%;
  max-width: 600px;
}

.card-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--surface-hover);
}

.card-header-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
}

.post-type-selector {
  display: flex;
  justify-content: space-around;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--surface-hover);
}

.button {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.button .icon {
  font-size: var(--font-size-xl);
}

.card-content {
  padding: var(--spacing-lg);
}

.field {
  margin-bottom: var(--spacing-lg);
}

.label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
}

.textarea {
  min-height: 150px;
  padding: var(--spacing-md);
  font-size: var(--font-size-base);
}

.help {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
}

.file-input-wrapper {
  position: relative;
  width: 100%;
  height: 150px;
  border: 2px dashed var(--surface-hover);
  border-radius: var(--radius-lg);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.file-input-wrapper:hover {
  border-color: var(--primary);
  background-color: var(--surface-hover);
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-input-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-secondary);
}

.file-input-label .icon {
  font-size: var(--font-size-2xl);
}

.selected-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  margin-top: var(--spacing-sm);
  background-color: var(--surface-hover);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
}

.delete {
  position: absolute;
  right: var(--spacing-md);
  top: var(--spacing-md);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.delete:hover {
  color: var(--danger);
}

@media (max-width: 768px) {
  .modal-content {
    padding: var(--spacing-sm);
    margin: var(--spacing-sm);
  }

  .add-post-card {
    margin: var(--spacing-md);
  }

  .post-type-selector {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .button {
    width: 100%;
    justify-content: center;
  }
}
</style>
