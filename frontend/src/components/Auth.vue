<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useCookies } from "vue3-cookies";

const serverURL = import.meta.env.VITE_BACKEND_URL;
const { cookies } = useCookies();

const props = defineProps(["showModal"]);
const emit = defineEmits(["updateShowModal", "updateLoggedIn"]);

const registerActive = ref(false);

const username = ref("");
const password = ref("");
const confirmPassword = ref("");
const isLoading = ref(false);

const closeModal = () => {
  emit("updateShowModal", false);
};

onMounted(() => {
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeModal();
    }
  });
});

const submitForm = async () => {
  if (!username.value || !password.value) {
    alert("Please fill in all fields");
    return;
  }
  if (registerActive.value) {
    if (password.value !== confirmPassword.value) {
      alert("Passwords do not match");
      return;
    }
  }

  const fetchURL = registerActive.value
    ? `${serverURL}/api/register`
    : `${serverURL}/api/token`;
  const response = await fetch(fetchURL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: username.value,
      password: password.value,
    }),
  });

  const data = await response.json();
  if (data.error) {
    alert(data.error);
    return;
  }

  if (data.detail || data.non_field_errors) {
    alert(data.detail ? data.detail : data.non_field_errors);
    username.value = "";
    password.value = "";
    confirmPassword.value = "";
    return;
  }
  cookies.set("refresh_token", data.refresh);
  cookies.set("access_token", data.access);
  localStorage.setItem("username", username.value);

  emit("updateLoggedIn", true);
  closeModal();
  username.value = "";
  password.value = "";
  confirmPassword.value = "";
  registerActive.value = false;
};
</script>

<template>
  <div v-if="showModal" class="modal-overlay">
    <div class="modal-container">
      <header class="modal-header">
        <h2 class="modal-title">Login</h2>
        <button
          class="close-modal"
          aria-label="close"
          @click="emit('updateShowModal', false)"
        >
          <v-icon name="io-close" />
        </button>
      </header>

      <div class="modal-content">
        <form @submit.prevent="submitForm">
          <div class="field">
            <label class="label">Username</label>
            <div class="control">
              <input
                v-model="username"
                type="text"
                class="input"
                placeholder="Enter your username"
              />
            </div>
          </div>

          <div class="field">
            <label class="label">Password</label>
            <div class="control">
              <input
                v-model="password"
                type="password"
                class="input"
                placeholder="Enter your password"
              />
            </div>
          </div>

          <div class="field">
            <div class="control">
              <button
                class="button is-primary is-fullwidth"
                type="submit"
                :disabled="isLoading"
              >
                {{ isLoading ? "Loading..." : "Login" }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.field {
  margin-bottom: var(--spacing-lg);
}

.label {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
}

.input {
  width: 100%;
  padding: var(--spacing-md);
  font-size: var(--font-size-base);
  background-color: var(--surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  transition: all var(--transition-fast);
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(var(--primary-rgb), 0.2);
}

.button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
