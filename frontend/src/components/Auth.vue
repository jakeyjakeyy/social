<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useCookies } from "vue3-cookies";

const serverURL = import.meta.env.VITE_BACKEND_URL;
const { cookies } = useCookies();

const props = defineProps(["showModal"]);
const emit = defineEmits(["updateShowModal"]);

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

  localStorage.setItem("token", data.token);
  closeModal();
};
</script>

<template>
  <div :class="['modal', showModal ? 'is-active' : '']">
    <div class="modal-background"></div>
    <div class="modal-content">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">
            {{ registerActive ? "Register" : "Login" }}
          </p>
        </header>

        <div class="card-content">
          <form @submit.prevent>
            <div class="field">
              <label class="label">Username</label>
              <div class="control">
                <input
                  class="input"
                  type="text"
                  placeholder="Username"
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
                  placeholder="Password"
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
                  placeholder="Confirm Password"
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
                  {{ registerActive ? "Register" : "Login" }}
                </button>
                <button
                  class="button is-info is-fullwidth"
                  @click="registerActive = !registerActive"
                >
                  {{
                    registerActive
                      ? "Already Have an account?"
                      : "Create an Account"
                  }}
                </button>
              </div>
            </div>
          </form>
          <button
            class="modal-close is-large"
            aria-label="close"
            @click="closeModal"
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
