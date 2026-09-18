import { defineStore } from 'pinia';
import api from '@/services/api';

export const useAcademicStore = defineStore('academic', {
  state: () => ({
    facultes: [],
    promotions: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchAll() {
      this.loading = true;
      this.error = null;
      try {
        const [resFac, resPromo] = await Promise.all([
          api.get('/admin/facultes'),
          api.get('/admin/promotions')
        ]);
        this.facultes = resFac.data.facultes;
        this.promotions = resPromo.data.promotions;
      } catch (err) {
        this.error = "Erreur lors du chargement des données académiques.";
      } finally {
        this.loading = false;
      }
    },

    // --- FACULTES ---
    async addFaculte(payload) {
      const res = await api.post('/admin/facultes', payload);
      this.facultes.push(res.data.faculte);
    },
    async updateFaculte(id, payload) {
      const res = await api.put(`/admin/facultes/${id}`, payload);
      const index = this.facultes.findIndex(f => f.id === id);
      if (index !== -1) this.facultes[index] = res.data.faculte;
    },
    async deleteFaculte(id) {
      await api.delete(`/admin/facultes/${id}`);
      this.facultes = this.facultes.filter(f => f.id !== id);
    },

    // --- PROMOTIONS ---
    async addPromotion(payload) {
      const res = await api.post('/admin/promotions', payload);
      this.promotions.push(res.data.promotion);
    },
    async updatePromotion(id, payload) {
      const res = await api.put(`/admin/promotions/${id}`, payload);
      const index = this.promotions.findIndex(p => p.id === id);
      if (index !== -1) this.promotions[index] = res.data.promotion;
    },
    async deletePromotion(id) {
      await api.delete(`/admin/promotions/${id}`);
      this.promotions = this.promotions.filter(p => p.id !== id);
    }
  }
});