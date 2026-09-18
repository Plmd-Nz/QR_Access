// src/stores/scan.js
import { defineStore } from 'pinia';
import api from '@/services/api'; // On importe ton instance API

export const useScanStore = defineStore('scan', {
    state: () => ({
        // Configuration du terminal de scan
        terminalConfig: {
            point_acces_id: null, // L'ID numérique réel de la BDD
            point_acces_nom: null, // Le nom pour l'affichage
        },
        // Liste des points d'accès récupérés depuis le Backend
        locations: [],
        // Les types de scan peuvent rester fixes car ils définissent la logique visuelle
        scanTypes: [
            { title: 'Entrée (Vérification de Présence)', value: 'ENTREE' },
            { title: 'Sortie (Décompte de Présence)', value: 'SORTIE' },
            { title: 'Paiement (Validation de Transaction)', value: 'PAIEMENT' },
        ],
        loading: false
    }),
    
    actions: {
        /**
         * Récupère les vrais points d'accès depuis la base de données
         */
        async fetchLocations() {
            this.loading = true;
            try {
                const response = await api.get('/scan/points_acces');
                // On transforme les données pour qu'elles soient compatibles avec les sélecteurs Vuetify
                this.locations = response.data.data.map(p => ({
                    title: p.nom,
                    value: p.id // On utilise l'ID réel ici
                }));
            } catch (error) {
                console.error("Erreur lors du chargement des points d'accès:", error);
            } finally {
                this.loading = false;
            }
        },

        /**
         * Sauvegarde la configuration réelle
         */
        saveConfiguration(pointId, scanType) {
            const selectedLocation = this.locations.find(l => l.value === pointId);
            
            this.terminalConfig.point_acces_id = pointId;
            this.terminalConfig.point_acces_nom = selectedLocation ? selectedLocation.title : 'Inconnu';
            this.terminalConfig.scanType = scanType;
            
            // Persistance
            localStorage.setItem('AcessChoix', JSON.stringify(this.terminalConfig));
        },
        
        loadConfiguration() {
            const config = localStorage.getItem('AcessChoix');
            if (config) {
                this.terminalConfig = JSON.parse(config);
            }
        },

        resetConfiguration() {
            this.terminalConfig = { point_acces_id: null, point_acces_nom: null, scanType: null };
            localStorage.removeItem('AcessChoix');
        }
    },
    
    getters: {
        // La configuration est valide si on a un ID numérique
        isConfigured: (state) => !!state.terminalConfig.point_acces_id,
        
        currentLocationTitle: (state) => state.terminalConfig.point_acces_nom || 'Non défini',
        
        currentScanTypeTitle: (state) => {
            const scanType = state.scanTypes.find(t => t.value === state.terminalConfig.scanType);
            return scanType ? scanType.title : 'Non défini';
        }
    }
});