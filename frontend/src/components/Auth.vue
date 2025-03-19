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
  <div :class="['modal', showModal ? 'is-active' : '']">
    <div class="modal-background"></div>
    <div class="modal-content">
      <div class="card auth-card">
        <header class="card-header">
          <p class="card-header-title">
            {{ registerActive ? "Create Account" : "Welcome Back" }}
          </p>
          <button
            class="delete"
            aria-label="close"
            @click="closeModal"
          ></button>
        </header>

        <div class="card-content">
          <form @submit.prevent>
            <div class="field">
              <label class="label">Username</label>
              <div class="control">
                <input
                  class="input"
                  type="text"
                  placeholder="Enter your username"
                  v-model="username"
                />
              </div>
            </div>
            <div class="field">
              <label class="label">Password</label>
              <div class="control">
                <input
                  class="input"
                  type="password"
                  placeholder="Enter your password"
                  v-model="password"
                />
              </div>
            </div>
            <div v-if="registerActive" class="field">
              <label class="label">Confirm Password</label>
              <div class="control">
                <input
                  class="input"
                  type="password"
                  placeholder="Confirm your password"
                  v-model="confirmPassword"
                />
              </div>
            </div>
            <div class="field">
              <div class="control">
                <button
                  class="button is-primary is-fullwidth"
                  @click="submitForm"
                >
                  {{ registerActive ? "Create Account" : "Sign In" }}
                </button>
                <button
                  class="button is-text is-fullwidth"
                  @click="registerActive = !registerActive"
                >
                  {{
                    registerActive
                      ? "Already have an account? Sign in"
                      : "Don't have an account? Create one"
                  }}
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
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--spacing-md);
  margin: var(--spacing-md);
  width: 100%;
  height: 100%;
}

.auth-card {
  width: 100%;
  max-width: 400px;
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

.input {
  width: 100%;
  padding: var(--spacing-md);
  font-size: var(--font-size-base);
}

.button.is-text {
  color: var(--text-secondary);
  background: none;
  border: none;
  padding: var(--spacing-sm) 0;
  margin-top: var(--spacing-sm);
}

.button.is-text:hover {
  color: var(--primary);
  background: none;
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

  .auth-card {
    margin: var(--spacing-md);
  }
}
</style>
