// src/services/api.js

import axios from 'axios';
import { useAuthStore } from '../stores/auth'; // Nous allons créer ce store juste après

// --- 1. Configuration de l'Instance Axios ---
const api = axios.create({
    baseURL: 'http://127.0.0.1:5000/api',
    // NE PAS METTRE DE CONTENT-TYPE ICI
});


// --- 2. Intercepteur de Requête (Injection du JWT) ---
// Cet intercepteur s'exécute avant chaque requête. Il ajoute le token JWT dans l'en-tête "Authorization".
api.interceptors.request.use(config => {
    const authStore = useAuthStore();
    if (authStore.isAuthenticated) {
        config.headers.Authorization = `Bearer ${authStore.token}`;
    }

    // AJOUTE CECI : Si c'est du FormData, on supprime le Content-Type 
    // pour laisser le navigateur mettre le boundary
    if (config.data instanceof FormData) {
        delete config.headers['Content-Type'];
    }
    
    return config;
}, error => Promise.reject(error));

// --- 3. Intercepteur de Réponse (Gestion des Erreurs 401) ---
// Cet intercepteur s'exécute après la réception de la réponse.
api.interceptors.response.use(response => {
    return response;
}, error => {
    // Si l'API retourne une erreur 401 (Non autorisé)
    if (error.response && error.response.status === 401) {
        const authStore = useAuthStore();
        if (authStore.isAuthenticated) {
            // Déconnexion automatique si le token est invalide ou expiré
            authStore.logout();
            // Rediriger l'utilisateur vers la page de connexion (ce sera fait au niveau du store)
        }
    }
    return Promise.reject(error);
});

export default api;