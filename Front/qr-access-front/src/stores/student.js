// src/stores/student.js
import { defineStore } from 'pinia';
import api from '@/services/api';

export const useStudentStore = defineStore('student', {
    state: () => ({
        students: [],
        loading: false,
        error: null,
    }),

    actions: {
        async fetchStudents() {
            this.loading = true;
            try {
                const response = await api.get('/admin/etudiants');
                this.students = response.data.etudiants;
            } catch (err) {
                this.error = "Erreur de chargement des étudiants.";
            } finally {
                this.loading = false;
            }
        },

        async createStudent(formData) {
            this.loading = true;
            try {
                // On enlève le header manuel : Axios va le gérer tout seul avec le bon boundary
                const response = await api.post('/admin/etudiants', formData);

                await this.fetchStudents();
                return response.data; // On retourne toute la data pour récupérer card_url
            } catch (err) {
                console.error("Erreur Store:", err);
                throw err.response?.data?.message || "Erreur lors de l'inscription.";
            } finally {
                this.loading = false;
            }
        },

        async updateStudent(matricule, payload) {
            this.loading = true;
            try {
                // Ton back utilise le MATRICULE dans l'URL pour l'update
                const response = await api.put(`/admin/etudiants/${matricule}`, payload);
                await this.fetchStudents();
                return response.data;
            } catch (err) {
                throw err.response?.data?.message || "Erreur de mise à jour.";
            } finally {
                this.loading = false;
            }
        },

        async deleteStudent(matricule) {
            try {
                // Ton back utilise le MATRICULE pour la suppression
                await api.delete(`/admin/etudiants/${matricule}`);
                this.students = this.students.filter(s => s.matricule !== matricule);
            } catch (err) {
                throw err.response?.data?.message || "Erreur de suppression.";
            }
        }
    }
});