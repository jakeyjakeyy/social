import "./assets/main.css";

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import { OhVueIcon, addIcons } from "oh-vue-icons";
import {
  CoHamburgerMenu,
  BiHeart,
  BiHeartFill,
  RiRepeat2Line,
  RiRepeat2Fill,
  FaMoon,
  FaSun,
  FaGripLinesVertical,
} from "oh-vue-icons/icons";

addIcons(
  CoHamburgerMenu,
  BiHeart,
  BiHeartFill,
  RiRepeat2Fill,
  RiRepeat2Line,
  FaMoon,
  FaSun,
  FaGripLinesVertical
);

const app = createApp(App);

app.use(router);

app.component("v-icon", OhVueIcon);

app.mount("#app");
