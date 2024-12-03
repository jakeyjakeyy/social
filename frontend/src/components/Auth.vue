<script setup lang="ts">
import { ref, onMounted } from "vue";

const props = defineProps(["showModal"]);
const emit = defineEmits(["updateShowModal"]);

const registerActive = ref(false);

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
                <input class="input" type="text" placeholder="Username" />
              </div>
            </div>
            <div class="field">
              <label class="label">Password</label>
              <div class="control">
                <input class="input" type="password" placeholder="Password" />
              </div>
            </div>
            <div v-if="registerActive" class="field">
              <label class="label">Confirm Password</label>
              <div class="control">
                <input
                  class="input"
                  type="password"
                  placeholder="Confirm Password"
                />
              </div>
            </div>
            <div class="field">
              <div class="control">
                <button class="button is-primary is-fullwidth">
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
