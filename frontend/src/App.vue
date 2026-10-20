<template>
  <div id="app">
    <router-view />
    <ThemeToggle />
  </div>
</template>

<script setup>
import ThemeToggle from '@/components/ui/ThemeToggle.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  width: 100%;
  height: 100vh;
  background: var(--app-bg);
  color: var(--app-text);
  transition: background-color 0.3s ease, color 0.3s ease;
}

:root[data-theme='dark'] {
  --app-bg: #0b1020;
  --app-bg-soft: #121a2f;
  --app-text: #eaf0ff;
  --app-text-soft: #b8c2df;
  --app-border: rgba(180, 198, 245, 0.22);
  --app-card: rgba(18, 26, 47, 0.78);
}

:root[data-theme='light'] {
  --app-bg: #f7f9ff;
  --app-bg-soft: #ffffff;
  --app-text: #1f2937;
  --app-text-soft: #4b5563;
  --app-border: rgba(15, 23, 42, 0.12);
  --app-card: rgba(255, 255, 255, 0.92);
}

/* Light theme: invert dark-hardcoded elements */
:root[data-theme='light'] .invert-on-light {
  filter: invert(1) hue-rotate(180deg);
}

:root[data-theme='light'] .invert-on-light img,
:root[data-theme='light'] .invert-on-light video,
:root[data-theme='light'] .invert-on-light canvas,
:root[data-theme='light'] .invert-on-light svg image,
:root[data-theme='light'] .invert-on-light .no-invert,
:root[data-theme='light'] .invert-on-light #template-onlyoffice-editor,
:root[data-theme='light'] .invert-on-light #template-onlyoffice-editor iframe,
:root[data-theme='light'] .invert-on-light #onlyoffice-editor,
:root[data-theme='light'] .invert-on-light #onlyoffice-editor iframe,
:root[data-theme='light'] .invert-on-light #document-library-onlyoffice-editor,
:root[data-theme='light'] .invert-on-light #document-library-onlyoffice-editor iframe,
:root[data-theme='light'] .invert-on-light #script-onlyoffice-editor,
:root[data-theme='light'] .invert-on-light #script-onlyoffice-editor iframe,
:root[data-theme='light'] .invert-on-light .preview-onlyoffice-container,
:root[data-theme='light'] .invert-on-light .preview-onlyoffice-container iframe,
:root[data-theme='light'] .invert-on-light .inline-preview,
:root[data-theme='light'] .invert-on-light .inline-preview iframe,
:root[data-theme='light'] .invert-on-light .editor-container,
:root[data-theme='light'] .invert-on-light .editor-container iframe {
  filter: invert(1) hue-rotate(180deg);
}

</style>
