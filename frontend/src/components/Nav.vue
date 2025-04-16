<script setup lang="ts">
import Auth from "./Auth.vue";
import AddPost from "./AddPost.vue";
import ThemeSelector from "./ThemeSelector.vue";
import { onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import { deleteTokens, checkToken } from "@/utils/RefreshToken";
import Notifications from "./Notifications.vue";
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
    checkNavIsMobile();
  });

  checkNavIsMobile();

  theme.value = localStorage.getItem("theme") || "dark";
});

onUnmounted(() => {
  window.removeEventListener("resize", checkNavIsMobile);
});

const navItems = [
  { name: "Home", path: "/" },
  { name: "Profile", path: "/profile" },
  { name: loggedIn.value ? "Logout" : "Login", path: "/auth" },
];

function checkNavIsMobile() {
  if (screen.value < 768) {
    navIsMobile.value = true;
  } else {
    navIsMobile.value = false;
  }
}

const navigateTo = (path: string) => {
  if (path === "/auth") {
    switch (loggedIn.value) {
      case true:
        loggedIn.value = false;
        deleteTokens();
        localStorage.removeItem("username");
        navItems[2].name = "Login";
        window.location.reload();
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
  // window.location.reload();
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
  <nav class="nav">
    <div class="container nav-container">
      <div class="nav-brand nav-item">
        <button @click="navigateTo('/')" class="brand-link">
          <v-icon name="ri-chat-smile-2-fill" scale="1.5" class="brand-icon" />
          <span class="brand-text">Social</span>
        </button>
      </div>

      <div class="nav-menu" :class="{ 'is-active': showMobileNav }">
        <div class="nav-start">
          <button @click="navigateTo('/')" class="nav-item">
            <v-icon name="ri-home-5-line" />
            <span>Home</span>
          </button>
          <button v-if="loggedIn" @click="navigateTo('/profile')" class="nav-item">
            <v-icon name="ri-user-line" />
            <span>Profile</span>
          </button>
        </div>

        <div class="nav-end">
          <button v-if="loggedIn" class="nav-item" @click="showAddPost = true">
            <v-icon name="ri-add-line" />
            <span>New Post</span>
          </button>
          <button class="nav-item" @click="navigateTo('/auth')">
            <v-icon :name="loggedIn ? 'ri-logout-box-line' : 'ri-login-box-line'" />
            <span>{{ loggedIn ? "Logout" : "Login" }}</span>
          </button>
          <ThemeSelector @toggle-theme="toggleTheme" />
          <Notifications v-if="loggedIn && !navIsMobile" class="nav-item" />
        </div>
      </div>

      <div class="nav-burger" @click="showMobileNav = !showMobileNav">
        <v-icon name="co-hamburger-menu" scale="1.5" />
        <Notifications v-if="loggedIn && navIsMobile" class="nav-item" />
      </div>
    </div>
  </nav>

  <AddPost v-if="showAddPost" @closeAddPostModal="toggleAddPostModal" :is-reply="false" />
  <Auth :showModal="showModal" @updateShowModal="updateShowModal" @updateLoggedIn="updateLoggedIn" />
  <div class="notification is-success" v-if="showNotification">
    <button class="delete"></button>
    <strong>Success!</strong> Post added successfully.
  </div>
</template>

<style scoped>
.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(8px);
  background-color: rgba(var(--surface), 0.8);
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
  color: var(--text-primary);
}

.brand-icon {
  color: var(--primary);
}

.brand-text {
  font-size: var(--font-size-xl);
  font-weight: 700;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.nav-start,
.nav-end {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-full);
  color: var(--text-primary);
  text-decoration: none;
  transition: background-color var(--transition-fast);
  cursor: pointer;
}

.nav-item:hover {
  background-color: var(--surface-hover);
}

.nav-item .icon {
  font-size: var(--font-size-xl);
}

.nav-burger {
  display: none;
  cursor: pointer;
  padding: var(--spacing-sm);
  border-radius: var(--radius-full);
  transition: background-color var(--transition-fast);
}

.nav-burger:hover {
  background-color: var(--surface-hover);
}

.notification {
  position: fixed;
  bottom: var(--spacing-lg);
  right: var(--spacing-lg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
}

.nav-brand {
  cursor: pointer;
}

@media (max-width: 768px) {
  .nav-menu {
    position: fixed;
    top: 96px;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--surface);
    flex-direction: column;
    padding: var(--spacing-lg);
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
    height: 100vh;
  }

  .nav-menu.is-active {
    transform: translateX(0);
  }

  .nav-start,
  .nav-end {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }

  .nav-item {
    width: 100%;
    padding: var(--spacing-md);
  }

  .nav-burger {
    display: flex;
    justify-content: flex-end;
  }
}
</style>
