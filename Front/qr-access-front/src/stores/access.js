import { defineStore } from 'pinia';
import api from '@/services/api';

export const useAccessStore = defineStore('access', {
  state: () => ({
    pointsAcces: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchPoints() {
      this.loading = true;
      try {
        const res = await api.get('/admin/points_acces');
        this.pointsAcces = res.data.points_acces;
      } catch (err) {
        this.error = "Erreur lors du chargement des points d'accès.";
      } finally {
        this.loading = false;
      }
    },

    async addPoint(payload) {
      const res = await api.post('/admin/points_acces', payload);
      this.pointsAcces.push(res.data.point_acces);
    },

    async updatePoint(id, payload) {
      const res = await api.put(`/admin/points_acces/${id}`, payload);
      const index = this.pointsAcces.findIndex(p => p.id === id);
      if (index !== -1) this.pointsAcces[index] = res.data.point_acces;
    },

    async deletePoint(id) {
      await api.delete(`/admin/points_acces/${id}`);
      this.pointsAcces = this.pointsAcces.filter(p => p.id !== id);
    }
  }
});