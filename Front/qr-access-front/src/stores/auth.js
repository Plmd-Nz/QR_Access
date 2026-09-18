// src/stores/auth.js

import { defineStore } from 'pinia';
import api from '../services/api'; // Importation de l'instance Axios configurée
import router from '../router'; // Pour la redirection après déconnexion

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('qr_access_token') || null,
        user: JSON.parse(localStorage.getItem('qr_access_user')) || null,
    }),

    getters: {
        // Dérivé de l'état : l'utilisateur est-il connecté ?
        isAuthenticated: (state) => !!state.token,
    },

    actions: {
        // Action de connexion (appel POST /api/auth/login)
        async login(credentials) {
            try {
                // Assurez-vous que 'credentials' contient 'nom_utilisateur' et 'mot_de_passe'
                const response = await api.post('/auth/login', credentials);

                // ATTENTION : Le backend renvoie 'access_token' et 'admin_name' (pas 'user_info').
                // On utilise une variable temporaire pour correspondre au backend.
                const { access_token, admin_name } = response.data;

                // Mettre à jour l'état local (Le store gère l'info sous le nom 'user')
                this.token = access_token;
                // Crée un objet utilisateur pour le store à partir de l'information reçue
                const user_info = { name: admin_name, nom_complet: admin_name };
                this.user = user_info;

                // Persister l'état dans le Local Storage
                localStorage.setItem('qr_access_token', access_token);
                localStorage.setItem('qr_access_user', JSON.stringify(user_info));

                // Redirection vers le tableau de bord Admin
                router.push({ name: 'AdminDashboard' });
                return true;

            } catch (error) {
                // Renvoyer l'erreur pour que le composant de connexion puisse l'afficher
                throw error.response?.data?.message || "Erreur de connexion inconnue.";
            }
        },

        // Action de déconnexion
        logout() {
            this.token = null;
            this.user = null;
            localStorage.removeItem('qr_access_token');
            localStorage.removeItem('qr_access_user');


            // Vérifie que le token est bien dans le localStorage avant la redirection
            if (this.token) {
                router.push({ name: 'AdminDashboard' });
            } else {
                throw new Error("Le token n'a pas été récupéré correctement.");
            }

        }
    }
});