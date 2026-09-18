// src/main.js

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify' // Importe la configuration Vuetify
import { useAuthStore } from './stores/auth' // Importe le store d'authentification
import { useScanStore } from './stores/scan' // Importe le store de configuration du scan


const app = createApp(App)
const pinia = createPinia()

app.use(pinia) // 1. Pinia doit être monté en premier

// --- Initialisation des Stores et des États ---

// Initialisation du Auth Store pour vérifier le token au démarrage
const authStore = useAuthStore()
// Tenter de récupérer le token et l'utilisateur du localStorage
authStore.token = localStorage.getItem('qr_access_token')
const userString = localStorage.getItem('qr_access_user');
if (userString) {
    try {
        authStore.user = JSON.parse(userString);
    } catch (e) {
        console.error("Erreur de parsing de l'utilisateur stocké.", e);
        authStore.user = {};
    }
}

// Initialisation du Scan Store pour récupérer la configuration du terminal
const scanStore = useScanStore()
scanStore.loadConfiguration()

// --- Montage de l'Application ---

app.use(router)
app.use(vuetify)

app.mount('#app')