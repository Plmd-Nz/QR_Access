<template>
  <v-container fluid class="py-6">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4">Tableau de Bord Général</h1>
      <v-spacer></v-spacer>
      <v-btn 
        color="secondary"  
        class="mr-2"
        @click="fetchDashboardStats" 
        :loading="loading"
      >
        Actualiser
      </v-btn>
      <v-btn 
        icon="mdi-refresh" 
        variant="text" 
        @click="fetchDashboardStats" 
        :loading="loading"
      ></v-btn>
    </div>

    <v-row>
      <v-col cols="12" sm="6" lg="3">
        <v-card class="elevation-4 pa-4" color="primary" theme="dark">
          <div class="d-flex align-center">
            <v-icon size="48" class="mr-4">mdi-account-group</v-icon>
            <div>
              <p class="text-subtitle-1">Étudiants</p>
              <p class="text-h5 font-weight-bold">{{ stats.total_etudiants }}</p>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" lg="3">
        <v-card class="elevation-4 pa-4" color="indigo-darken-1" theme="dark">
          <div class="d-flex align-center">
            <v-icon size="48" class="mr-4">mdi-cash-multiple</v-icon>
            <div>
              <p class="text-subtitle-1">Total Perçu</p>
              <p class="text-h5 font-weight-bold">{{ formatCurrency(stats.total_paiements_usd) }}</p>
            </div>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" lg="3">
        <v-card class="elevation-4 pa-4" color="teal-darken-1" theme="dark">
          <div class="d-flex align-center">
            <v-icon size="48" class="mr-4">mdi-calendar-check</v-icon>
            <div>
              <p class="text-subtitle-1">Présences Jour</p>
              <p class="text-h5 font-weight-bold">{{ stats.presences_du_jour }}</p>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" lg="3">
        <v-card class="elevation-4 pa-4" color="orange-darken-1" theme="dark">
          <div class="d-flex align-center">
            <v-icon size="48" class="mr-4">mdi-domain</v-icon>
            <div>
              <p class="text-subtitle-1">Facultés / Promos</p>
              <p class="text-h5 font-weight-bold">{{ stats.total_facultes }} / {{ stats.total_promotions }}</p>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-8">
      <v-col cols="12" lg="8">
        <v-card class="elevation-4 fill-height">
          <v-card-title class="bg-primary text-white d-flex align-center">
            Répartition par Faculté
            <v-spacer></v-spacer>
            <v-icon>mdi-chart-bar</v-icon>
          </v-card-title>
          <v-card-text class="pa-4">
            <div v-if="stats.top_facultes_etudiants && stats.top_facultes_etudiants.length">
              <div v-for="(fac, index) in stats.top_facultes_etudiants" :key="index" class="mb-4">
                <div class="d-flex justify-space-between mb-1">
                  <span>{{ fac.nom }}</span>
                  <span class="font-weight-bold">{{ fac.count }} étudiants</span>
                </div>
                <v-progress-linear
                  :model-value="(fac.count / stats.total_etudiants) * 100"
                  color="primary"
                  height="12"
                  rounded
                ></v-progress-linear>
              </div>
            </div>
            <div v-else class="text-center py-8 text-grey">
              Aucune donnée de répartition disponible.
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="4">
        <v-card class="elevation-4 fill-height">
          <v-card-title class="bg-grey-darken-3 text-white">Alertes Système</v-card-title>
          <v-list density="comfortable">
            <v-list-item 
              prepend-icon="mdi-cash-register" 
              title="Paiements du jour" 
              :subtitle="formatCurrency(stats.paiements_du_jour_usd)"
              color="success"
            ></v-list-item>
            <v-list-item 
              prepend-icon="mdi-map-marker-radius" 
              title="Points d'accès actifs" 
              :subtitle="stats.total_points_acces + ' terminaux configurés'"
            ></v-list-item>
            <v-list-item 
              prepend-icon="mdi-check-circle" 
              title="Statut Serveur" 
              subtitle="Opérationnel" 
              color="success"
            ></v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <v-overlay v-model="loading" class="align-center justify-center" persistent>
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </v-overlay>

    <v-snackbar v-model="showError" color="error" timeout="5000">
      {{ errorMessage }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';

const loading = ref(false);
const showError = ref(false);
const errorMessage = ref(null);

// Initialisation avec les clés exactes de ton JSON Back-end
const stats = ref({
  total_etudiants: 0,
  total_facultes: 0,
  total_promotions: 0,
  total_points_acces: 0,
  total_paiements_usd: "0",
  presences_du_jour: 0,
  paiements_du_jour_usd: "0",
  top_facultes_etudiants: []
});

const formatCurrency = (value) => {
  const amount = parseFloat(value) || 0;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
};

const fetchDashboardStats = async () => {
  loading.value = true;
  try {
    const response = await api.get('/admin/dashboard_stats');
    stats.value = response.data.stats;
  } catch (error) {
    errorMessage.value = error.response?.data?.message || "Erreur de connexion aux statistiques.";
    showError.value = true;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDashboardStats();
});
</script>

<style scoped>
.fill-height {
  height: 100%;
}
</style>