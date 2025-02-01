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
const showNotification = ref(false);

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
  } else if (path === "/profile") {
    path = `/@${localStorage.getItem("username")}`;
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
  window.location.reload();
};

const toggleAddPostModal = (value: boolean) => {
  showAddPost.value = false;
  if (value) {
    showNotification.value = true;
    setTimeout(() => {
      showNotification.value = false;
    }, 3000);
  }
};
</script>

<template>
  <div class="menu">
    <p class="menu-label">Navigation</p>
    <ul class="menu-list">
      <li @click="navigateTo('/')"><a>Home</a></li>
      <li v-if="loggedIn" @click="navigateTo('/profile')"><a>Profile</a></li>
    </ul>
    <p v-if="loggedIn" class="menu-label">Posts</p>
    <ul v-if="loggedIn" class="menu-list">
      <li @click="showAddPost = true"><a>Add Post</a></li>
    </ul>
    <p class="menu-label">Account</p>
    <ul class="menu-list">
      <li @click="navigateTo('/auth')">
        <a>{{ loggedIn ? "Logout" : "Login" }}</a>
      </li>
    </ul>
  </div>
  <AddPost v-if="showAddPost" @closeAddPostModal="toggleAddPostModal" />
  <Auth
    :showModal
    @updateShowModal="updateShowModal"
    @updateLoggedIn="updateLoggedIn"
  />
  <div class="notification is-success" v-if="showNotification">
    <button class="delete"></button>
    <strong>Success!</strong> Post added successfully.
  </div>
</template>

<style scoped>
.menu {
  width: 20vw;
}
/* .nav {
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
} */

.notification {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
}
</style>
