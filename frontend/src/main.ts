import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Import Tailwind CSS / Global styles
import './assets/main.css'

const app = createApp(App)

// 1. Install Pinia first (so router guards can access authStore)
app.use(createPinia())

// 2. Install Vue Router
app.use(router)

// 3. Mount to index.html
app.mount('#app')