<template>
  <v-container class="fill-height bg-grey-lighten-4" fluid>
    <v-row align="center" justify="center" class="mt-n12">
      <v-col cols="12" class="text-center mb-10">
        <v-icon color="primary" size="64" class="mb-4">mdi-Check-network</v-icon>
        <h1 class="text-h4 font-weight-black text-primary mb-2">Initialisation du Terminal</h1>
        <p class="text-h6 text-grey-darken-1">Où ce scanner est-il installé actuellement ?</p>
      </v-col>

      <v-col cols="12" md="10" lg="9">
        <v-row v-if="scanStore.loading" justify="center">
          <v-col cols="12" class="text-center">
            <v-progress-linear indeterminate color="primary" height="6" rounded></v-progress-linear>
            <p class="mt-4 text-button">Synchronisation avec la base de données...</p>
          </v-col>
        </v-row>

        <v-row v-else justify="center">
          <v-col 
            v-for="point in scanStore.locations" 
            :key="point.value" 
            cols="12" 
            sm="6" 
            md="4"
          >
            <v-card
              @click="selectAccessPoint(point)"
              class="point-card pa-6 text-center d-flex flex-column align-center justify-center"
              elevation="4"
              hover
              height="220"
              rounded="xl"
            >
              <v-avatar color="primary-lighten-5" size="80" class="mb-4">
                <v-icon size="40" color="primary">
                  {{ getIconForPoint(point.title) }}
                </v-icon>
              </v-avatar>
              
              <div class="text-h5 font-weight-bold text-grey-darken-3">{{ point.title }}</div>
              <div class="text-caption text-uppercase mt-2 text-primary font-weight-bold">
                Cliquer pour activer
              </div>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-if="!scanStore.loading && scanStore.locations.length === 0">
          <v-col cols="12" md="6" class="mx-auto">
            <v-alert
              type="error"
              variant="flat"
              icon="mdi-database-off"
              title="Aucune donnée"
            >
              Aucun point d'accès n'a été trouvé dans le système. Veuillez en créer un dans l'administration.
            </v-alert>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useScanStore } from '@/stores/scan';

const router = useRouter();
const scanStore = useScanStore();

onMounted(async () => {
  // On récupère uniquement les points d'accès réels de la BDD
  await scanStore.fetchLocations();
});

/**
 * Capture les infos et redirige vers le scan
 */
const selectAccessPoint = (point) => {
  // On injecte les infos dans le store (Lieu + Type 'ENTREE' par défaut)
  scanStore.saveConfiguration(point.value, 'ENTREE');
  
  // Direction immédiate vers l'interface de scan réelle
  router.push({ name: 'ScanInterface' });
};

/**
 * Détermination visuelle automatique
 */
const getIconForPoint = (name) => {
  const n = name.toLowerCase();
  if (n.includes('porte') || n.includes('entrée') || n.includes('gate')) return 'mdi-door-open';
  if (n.includes('bibli')) return 'mdi-library';
  if (n.includes('cafet') || n.includes('cantine')) return 'mdi-food-fork-drink';
  if (n.includes('auditoire') || n.includes('salle') || n.includes('classe')) return 'mdi-account-group';
  if (n.includes('labo')) return 'mdi-flask';
  return 'mdi-map-marker-check'; 
};
</script>

<style scoped>
.point-card {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 2px solid transparent;
  background-color: white !important;
}

.point-card:hover {
  transform: translateY(-8px);
  border-color: #1976D2; /* Couleur primaire */
  background-color: #F5F9FF !important;
}

.text-primary {
  color: #1976D2 !important;
}
</style>