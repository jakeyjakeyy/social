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
  FaRegularTrashAlt,
  BiChatLeft,
  BiCamera,
  IoClose,
  RiText,
  RiMarkdownLine,
  RiImageLine,
  RiUploadCloudLine,
  RiChatSmile2Fill,
  RiHome5Line,
  RiUserLine,
  RiAddLine,
  RiLogoutBoxLine,
  RiLoginBoxLine,
} from "oh-vue-icons/icons";

addIcons(
  CoHamburgerMenu,
  BiHeart,
  BiHeartFill,
  RiRepeat2Fill,
  RiRepeat2Line,
  FaMoon,
  FaSun,
  FaGripLinesVertical,
  FaRegularTrashAlt,
  BiChatLeft,
  BiCamera,
  IoClose,
  RiText,
  RiMarkdownLine,
  RiImageLine,
  RiUploadCloudLine,
  RiChatSmile2Fill,
  RiHome5Line,
  RiUserLine,
  RiAddLine,
  RiLogoutBoxLine,
  RiLoginBoxLine
);

const app = createApp(App);

app.use(router);

app.component("v-icon", OhVueIcon);

app.mount("#app");
