import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { Quasar, Notify, Dialog } from 'quasar'
import quasarIconSet from 'quasar/icon-set/material-icons.js'
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/src/css/index.sass'

import './assets/main.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.use(Quasar, {
  plugins: { Notify, Dialog },
  iconSet: quasarIconSet,
  config: {
    notify: {
      position: 'top-right',
      timeout: 3000,
    },
  },
})

app.mount('#app')
