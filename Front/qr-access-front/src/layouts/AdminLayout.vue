<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-app-bar-title>QR-ACCESS - Administration</v-app-bar-title>
      <v-spacer></v-spacer>

      <v-btn icon @click="toggleTheme">
        <v-icon>{{ themeIcon }}</v-icon>
      </v-btn>

      <v-btn text @click="handleLogout">Déconnexion</v-btn>
    </v-app-bar>

    <v-navigation-drawer app permanent expand-on-hover width="250">
      <v-list-item class="text-center pa-4">
        <v-list-item-title class="text-h6">
          {{ authStore.user ? (authStore.user.nom_complet || authStore.user.name) : 'Administrateur' }}
        </v-list-item-title>
        <v-list-item-subtitle>
          <v-badge dot color="success" inline></v-badge>
          Connecté
        </v-list-item-subtitle>
      </v-list-item>

      <v-divider></v-divider>

      <v-list dense nav>
        <v-list-item link :to="{ name: 'AdminDashboard' }">
          <template v-slot:prepend>
            <v-icon>mdi-view-dashboard</v-icon>
          </template>
          <v-list-item-title>Tableau de Bord</v-list-item-title>
        </v-list-item>

        <v-list-item link :to="{ name: 'StudentsAdmin' }">
          <template v-slot:prepend>
            <v-icon>mdi-account-group</v-icon>
          </template>
          <v-list-item-title>Étudiants</v-list-item-title>
        </v-list-item>

        <v-list-item link :to="{ name: 'AcademicConfig' }">
          <template v-slot:prepend>
            <v-icon>mdi-domain</v-icon>
          </template>
          <v-list-item-title>Structure Académique</v-list-item-title>
        </v-list-item>

        <v-list-item link :to="{ name: 'PaymentsAdmin' }">
          <template v-slot:prepend>
            <v-icon>mdi-cash-multiple</v-icon>
          </template>
          <v-list-item-title>Paiements</v-list-item-title>
        </v-list-item>

        <v-list-item link :to="{ name: 'ReportsAdmin' }">
          <template v-slot:prepend>
            <v-icon>mdi-file-chart</v-icon>
          </template>
          <v-list-item-title>Rapports</v-list-item-title>
        </v-list-item>

        <v-list-item link :to="{ name: 'ScanConfig' }">
          <template v-slot:prepend>
            <v-icon color="orange-darken-2">mdi-qrcode-scan</v-icon>
          </template>
          <v-list-item-title>Config. Scanner</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <router-view />
    </v-main>

    <v-footer app color="primary" class="d-flex justify-center text-white">
      <v-container fluid class="text-center pa-3">
        <p>
          &copy; Plmd_Nz - {{ new Date().getFullYear() }} - Tous droits réservés.
        </p>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useTheme } from 'vuetify';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const theme = useTheme();
const router = useRouter();

const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark';
};

const themeIcon = computed(() =>
  theme.global.current.value.dark ? 'mdi-white-balance-sunny' : 'mdi-weather-night'
);

// Correction de la déconnexion pour ignorer l'erreur de token
const handleLogout = async () => {
  try {
    // On tente l'appel au store
    await authStore.logout();
  } catch (error) {
    // Si le store plante (erreur de token), on affiche l'erreur en console
    console.warn("Logout store error, forcing redirection:", error);
    
    // On force quand même le nettoyage local si nécessaire
    localStorage.removeItem('token'); 
    localStorage.removeItem('user');
  } finally {
    // Dans tous les cas (succès ou erreur), on redirige vers le Login
    router.push({ name: 'Login' });
  }
};
</script>

<style scoped>
.v-app {
  min-height: 100vh;
}
</style>