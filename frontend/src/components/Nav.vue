<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

const showNavItems = ref(false);
const router = useRouter();

const navItems = [
  { name: "Home", path: "/" },
  { name: "Profile", path: "/profile" },
  { name: "Settings", path: "/settings" },
];

const toggleNavItems = () => {
  showNavItems.value = !showNavItems.value;
};

const navigateTo = (path: string) => {
  router.push(path);
};
</script>

<template>
  <div class="nav has-background-link" @click="toggleNavItems">
    nav

    <div v-if="showNavItems" class="nav-items">
      <div
        v-for="(item, index) in navItems"
        :key="index"
        class="nav-item"
        @click="navigateTo(item.path)"
      >
        {{ item.name }}
      </div>
    </div>
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
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-item {
  position: absolute;
  bottom: 0;
  padding: 0.5rem 1rem;
  background-color: white;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.3s;
}

.nav-item:nth-child(1) {
  transform: translate(-100%, 0);
}

.nav-item:nth-child(2) {
  transform: translate(0, -100%);
}

.nav-item:nth-child(3) {
  transform: translate(100%, 0);
}
</style>
