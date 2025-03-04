<script setup lang="ts">
import Auth from "./Auth.vue";
import AddPost from "./AddPost.vue";
import ThemeSelector from "./ThemeSelector.vue";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { deleteTokens, checkToken } from "@/utils/RefreshToken";
const showNavItems = ref(false);
const router = useRouter();
const showModal = ref(false);
const loggedIn = ref(checkToken());
const showAddPost = ref(false);
const showNotification = ref(false);
const screen = ref(window.innerWidth);
const navIsMobile = ref(false);
const showMobileNav = ref(false);
const theme = ref("dark");

onMounted(() => {
  window.addEventListener("resize", () => {
    screen.value = window.innerWidth;
  });

  if (screen.value < 768) {
    navIsMobile.value = true;
  }

  theme.value = localStorage.getItem("theme") || "dark";
});
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
  if (navIsMobile.value) {
    showMobileNav.value = false;
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

const toggleTheme = () => {
  theme.value = localStorage.getItem("theme") || "dark";
};
</script>

<template>
  <div
    class="menu has-background"
    v-if="(navIsMobile && showMobileNav) || !navIsMobile"
  >
    <ThemeSelector @toggle-theme="toggleTheme" />
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
  <AddPost
    v-if="showAddPost"
    @closeAddPostModal="toggleAddPostModal"
    :is-reply="false"
  />
  <Auth
    :showModal
    @updateShowModal="updateShowModal"
    @updateLoggedIn="updateLoggedIn"
  />
  <div class="notification is-success" v-if="showNotification">
    <button class="delete"></button>
    <strong>Success!</strong> Post added successfully.
  </div>
  <div
    v-if="navIsMobile"
    class="toggle-nav"
    @click="showMobileNav = !showMobileNav"
  >
    <span class="icon">
      <v-icon
        name="co-hamburger-menu"
        :color="theme === 'dark' ? 'white' : 'black'"
      />
    </span>
  </div>
</template>

<style scoped>
.menu {
  width: 20vw;
}

.notification {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

@media (max-width: 768px) {
  .menu {
    position: fixed;
    width: 100vw;
    height: 100vh;
    z-index: 10;
    padding-top: 3rem;
  }
  .toggle-nav {
    position: fixed;
    display: flex;
    justify-content: center;
    align-items: center;
    top: 0;
    right: 0;
    z-index: 10;
    color: white;
    border: 1px solid white;
    padding: 0.5rem;
  }
}
</style>
