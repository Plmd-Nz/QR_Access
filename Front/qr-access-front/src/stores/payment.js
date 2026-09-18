// src/stores/payment.js
import { defineStore } from 'pinia';
import api from '@/services/api';

export const usePaymentStore = defineStore('payment', {
    state: () => ({
        payments: [], 
        studentsForSelection: [], 
        loading: false,
        error: null,
    }),
    
    actions: {
        /**
         * LECTURE : Récupère tous les paiements
         */
        async fetchPayments() {
            this.loading = true;
            this.error = null;
            try {
                const response = await api.get('/admin/paiements');
                // Concordance : Flask renvoie {"paiements": [...]}
                this.payments = response.data.paiements || []; 
            } catch (err) {
                this.error = err.response?.data?.message || "Erreur de chargement des paiements.";
            } finally {
                this.loading = false;
            }
        },

        /**
         * UTILITAIRE : Liste des étudiants pour le Select
         */
        async fetchStudentsForSelection() {
            try {
                const response = await api.get('/admin/etudiants/select'); 
                // Concordance : Flask renvoie {"data": [{"id":..., "display_name":...}]}
                this.studentsForSelection = response.data.data || [];
            } catch (err) {
                console.error("Erreur liste étudiants:", err);
            }
        },

        /**
         * CRÉATION : Enregistre un nouveau paiement
         */
        async createPayment(formData) {
            this.loading = true;
            this.error = null;
            try {
                // Concordance : On mappe 'student_id' du front vers 'etudiant_id' du back
                const payload = {
                    etudiant_id: formData.student_id,
                    montant_paye: formData.montant_paye,
                    description: formData.description,
                    annee_academique: formData.annee_academique
                };
                
                const response = await api.post('/admin/paiements', payload);
                
                // On rafraîchit la liste pour avoir les données calculées du back (nom_etudiant, etc.)
                await this.fetchPayments();
                return response.data;
            } catch (err) {
                this.error = err.response?.data?.message || "Erreur lors de l'enregistrement.";
                throw this.error;
            } finally {
                this.loading = false;
            }
        },

        /**
         * MISE À JOUR : Modifie un paiement existant
         */
        async updatePayment(id, updateData) {
            this.loading = true;
            try {
                const response = await api.put(`/admin/paiements/${id}`, updateData);
                await this.fetchPayments(); // Rafraîchir la liste
                return response.data;
            } catch (err) {
                this.error = err.response?.data?.message || "Erreur lors de la modification.";
                throw this.error;
            } finally {
                this.loading = false;
            }
        },

        /**
         * SUPPRESSION : Supprime un paiement
         */
        async deletePayment(id) {
            if (!confirm("Voulez-vous vraiment supprimer ce paiement ? Cette action impactera le solde de l'étudiant.")) return;
            
            this.loading = true;
            try {
                await api.delete(`/admin/paiements/${id}`);
                // Mise à jour locale pour éviter un rechargement complet
                this.payments = this.payments.filter(p => p.id !== id);
            } catch (err) {
                this.error = err.response?.data?.message || "Erreur lors de la suppression.";
            } finally {
                this.loading = false;
            }
        }
    },

    getters: {
        filteredPayments: (state) => state.payments || []
    }
});