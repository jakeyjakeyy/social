<script setup lang="ts"></script>

<template>
  <footer>
    <div class="footer-license">
      <p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title"
          rel="cc:attributionURL" href="https://github.com/jakeyjakeyy/social">Social</a> by <a
          rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://jakerichards.info/">Jake
          Richards</a> is licensed under <a href="https://creativecommons.org/licenses/by-nc/4.0/?ref=chooser-v1"
          target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC 4.0<img
            style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
            src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img
            style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
            src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img
            style="height:22px!important;margin-left:3px;vertical-align:text-bottom;"
            src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""></a></p>
    </div>
    <div class="footer-icons">
      <div class="icon">
        <a href="https://www.github.com/jakeyjakeyy/social" aria-label="github" target="_blank">
          <v-icon name="fa-github" scale="1.25" />
        </a>
      </div>
    </div>

    <div class="footer-version">
      <p>v1.0.0</p>
    </div>
  </footer>
</template>

<style scoped>
footer {
  width: 100vw;
  height: 2.5rem;
  background-color: var(--surface);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: auto;
}

.footer-icons {
  display: flex;
  justify-content: center;
  align-items: center;
}

.footer-version {
  position: absolute;
  right: 1rem;
  font-size: smaller;
  color: var(--text);
}

.footer-license {
  position: absolute;
  left: 1rem;
  font-size: smaller;
}

.icon {
  width: 25px;
  height: 25px;
  margin: 0 0.5rem;
}

a {
  color: var(--text);
}

html,
body {
  height: 100%;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
</style>
