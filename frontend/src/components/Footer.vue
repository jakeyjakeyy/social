<script setup lang="ts"></script>

<template>
  <footer>
    <div class="footerIcons">
      <div class="icon">
        <a href="https://www.github.com/jakeyjakeyy" aria-label="github" target="_blank">
          <v-icon name="fa-github" scale="1.25" />
        </a>
      </div>
    </div>
    <div class="version">
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

.footerIcons {
  display: flex;
  justify-content: center;
  align-items: center;
}

.version {
  position: absolute;
  right: 1rem;
  font-size: smaller;
  color: var(--text);
}

.icon {
  width: 25px;
  height: 25px;
  margin: 0 0.5rem;
}

a {
  color: var(--text);
}

html, body {
  height: 100%;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
</style>
