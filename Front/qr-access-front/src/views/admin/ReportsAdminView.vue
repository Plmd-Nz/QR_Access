<template>
  <v-container>
    <div class="d-flex align-center mb-6">
      <v-icon icon="mdi-file-chart" size="large" color="primary" class="me-3"></v-icon>
      <h1 class="text-h4 font-weight-bold">Centre de Rapports Académiques</h1>
    </div>

    <v-alert v-if="academicStore.error" type="error" variant="tonal" class="mb-4">
      {{ academicStore.error }}
    </v-alert>

    <v-row>
      <v-col cols="12" md="6">
        <v-card border elevation="3" class="rounded-lg">
          <v-toolbar color="primary" density="compact">
            <v-toolbar-title class="text-body-1 font-weight-bold">
              <v-icon icon="mdi-account-check" class="me-2"></v-icon>
              Rapport d'Assiduité Journalier
            </v-toolbar-title>
          </v-toolbar>

          <v-card-text class="pt-6">
            <v-select
              v-model="filters.presence.promoId"
              :items="academicStore.promotions"
              item-title="nom"
              item-value="id"
              label="Sélectionner la Promotion"
              variant="outlined"
              prepend-inner-icon="mdi-school"
              :loading="academicStore.loading"
            ></v-select>

            <v-text-field
              v-model="filters.presence.date"
              type="date"
              label="Date du rapport"
              variant="outlined"
              prepend-inner-icon="mdi-calendar"
            ></v-text-field>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions class="pa-4">
            <v-btn
              block
              color="primary"
              variant="elevated"
              size="large"
              :loading="loadingBtn.presence"
              :disabled="!filters.presence.promoId"
              @click="downloadReport('presence')"
            >
              <v-icon icon="mdi-download" class="me-2"></v-icon>
              Générer la Liste d'Appel
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card border elevation="3" class="rounded-lg">
          <v-toolbar color="success" density="compact">
            <v-toolbar-title class="text-body-1 font-weight-bold">
              <v-icon icon="mdi-currency-usd" class="me-2"></v-icon>
              Audit des Paiements
            </v-toolbar-title>
          </v-toolbar>

          <v-card-text class="pt-6">
            <v-select
              v-model="filters.finance.promoId"
              :items="academicStore.promotions"
              item-title="nom"
              item-value="id"
              label="Sélectionner la Promotion"
              variant="outlined"
              prepend-inner-icon="mdi-school"
              :loading="academicStore.loading"
            ></v-select>
            
            <v-alert type="info" variant="tonal" density="compact" class="text-caption">
              Ce rapport liste les étudiants en règle ou insolvables selon le seuil configuré sur le serveur.
            </v-alert>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions class="pa-4">
            <v-btn
              block
              color="success"
              variant="elevated"
              size="large"
              :loading="loadingBtn.finance"
              :disabled="!filters.finance.promoId"
              @click="downloadReport('finance')"
            >
              <v-icon icon="mdi-file-pdf-box" class="me-2"></v-icon>
              Générer l'Audit Financier
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { reactive, onMounted } from 'vue';
import { useAcademicStore } from '@/stores/academic'; // Ajuste le chemin si besoin
import api from '@/services/api';

const academicStore = useAcademicStore();

const loadingBtn = reactive({
  presence: false,
  finance: false
});

const filters = reactive({
  presence: {
    promoId: null,
    date: new Date().toISOString().substr(0, 10)
  },
  finance: {
    promoId: null
  }
});

// Charger les données au montage si elles ne le sont pas déjà
onMounted(() => {
  if (academicStore.promotions.length === 0) {
    academicStore.fetchAll();
  }
});

const downloadReport = async (type) => {
  loadingBtn[type] = true;
  
  try {
    let endpoint = '';
    let params = {};
    let fileName = '';

    if (type === 'presence') {
      endpoint = '/admin/daily-call-list';
      params = { 
        promotion_id: filters.presence.promoId, 
        date: filters.presence.date 
      };
      fileName = `Liste_Appel_${filters.presence.date}.pdf`;
    } else {
      endpoint = '/admin/financial-status';
      params = { 
        promotion_id: filters.finance.promoId 
      };
      fileName = `Etat_Financier_Promo_${filters.finance.promoId}.pdf`;
    }

    const response = await api.get(endpoint, {
      params,
      responseType: 'blob' // CRITIQUE : Pour recevoir le PDF binaire
    });

    // Création du processus de téléchargement
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    
    // Nettoyage
    link.remove();
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error("Erreur téléchargement rapport:", error);
    // Tu peux ici ajouter un petit snackbar ou une alerte pour l'utilisateur
  } finally {
    loadingBtn[type] = false;
  }
};
</script>

<style scoped>
.v-card {
  transition: transform 0.2s;
}
.v-card:hover {
  transform: translateY(-4px);
}
</style>