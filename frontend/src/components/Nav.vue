<script setup lang="ts">
import Auth from "./Auth.vue";
import AddPost from "./AddPost.vue";
import { ref } from "vue";
import { useRouter } from "vue-router";
import { deleteTokens, checkToken } from "@/utils/RefreshToken";
const showNavItems = ref(false);
const router = useRouter();
const showModal = ref(false);
const loggedIn = ref(checkToken());
const showAddPost = ref(false);

const navItems = [
  { name: "Home", path: "/" },
  { name: "Profile", path: "/profile" },
  { name: loggedIn.value ? "Logout" : "Login", path: "/auth" },
];

const toggleNavItems = () => {
  showNavItems.value = !showNavItems.value;
};

const navigateTo = (path: string) => {
  if (path === "/auth") {
    switch (loggedIn.value) {
      case true:
        loggedIn.value = false;
        deleteTokens();
        localStorage.removeItem("username");
        navItems[2].name = "Login";
        break;
      case false:
        showModal.value = true;
        navItems[2].name = "Logout";
        navItems.push({ name: "Add Post", path: "/add-post" });
        break;
    }
    return;
  }
  router.push(path);
};

const updateShowModal = (value: boolean) => {
  showModal.value = value;
};
const updateLoggedIn = (value: boolean) => {
  loggedIn.value = value;
  if (value) {
    navItems[2].name = "Logout";
  } else {
    navItems[2].name = "Login";
  }
};
</script>

<template>
  <div class="nav-container">
    <div class="nav has-background-link" @click="toggleNavItems">
      nav

      <div v-if="showNavItems" class="nav-items">
        <div
          class="nav-item has-text-primary-bold has-background-info"
          @click="navigateTo('/')"
        >
          Home
        </div>
        <div
          class="nav-item has-text-primary-bold has-background-info"
          @click="navigateTo('/profile')"
        >
          Profile
        </div>
        <div
          v-if="loggedIn"
          class="nav-item has-text-primary-bold has-background-info"
          @click="showAddPost = true"
        >
          Add Post
        </div>
        <div
          :class="[
            'nav-item',
            'has-text-primary-bold',
            loggedIn ? 'has-background-danger' : 'has-background-info',
          ]"
          @click="navigateTo('/auth')"
        >
          {{ loggedIn ? "Logout" : "Login" }}
        </div>
      </div>
    </div>
    <AddPost v-if="showAddPost" @closeAddPostModal="showAddPost = false" />
    <Auth
      :showModal
      @updateShowModal="updateShowModal"
      @updateLoggedIn="updateLoggedIn"
    />
  </div>
</template>

<style scoped>
.nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.75rem;
  border-radius: 20px;
  cursor: pointer;
}

.nav-items {
  position: absolute;
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  bottom: 100%;
  left: 0;
}

.nav-item {
  bottom: 0;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.3s;
}
</style>
