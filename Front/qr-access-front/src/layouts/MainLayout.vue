<template>
  <v-app :theme="isDark ? 'dark' : 'light'" class="app-background">
    <v-app-bar 
      app 
      color="primary" 
      elevation="2" 
      class="mx-4  rounded-lg"
      style="width: calc(100% - 32px);"
    >
      <v-app-bar-title class="font-weight-bold ml-4">
        QR-ACCESS - Administration
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <v-btn variant="text" to="/" prepend-icon="mdi-qrcode-scan" class="hidden-sm-and-down">
        Scan
      </v-btn>

      <v-btn variant="text" to="/Accueil" prepend-icon="mdi-information" class="hidden-sm-and-down">
        À propos
      </v-btn>

      <v-divider vertical inset class="mx-2"></v-divider>

      <v-btn variant="elevated" color="secondary" to="/login" prepend-icon="mdi-lock">
        Admin
      </v-btn>

      <v-btn icon @click="toggleTheme" class="ml-2 mr-2">
        <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main class="main-container">
      <v-container fluid class="pa-4">
        <v-sheet 
          min-height="80vh" 
          rounded="xl" 
          elevation="1" 
          class="overflow-hidden bg-grey-lighten-4"
        >
          <router-view />
        </v-sheet>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue';

const isDark = ref(false);

const toggleTheme = () => {
  isDark.value = !isDark.value;
};
</script>

<style scoped>
/* Couleur de fond légère pour faire ressortir les éléments blancs */
.app-background {
  background-color: #f0f2f5 !important;
}

/* Espacement du contenu principal */
.main-container {
  padding-top: 60px !important; /* Laisse de la place pour la barre détachée */
  padding-bottom: 10px !important;
}

/* Style spécifique pour le footer flottant */
.footer-card {
  border: 1px solid rgba(0,0,0,0.05);
}

/* Adaptation pour le mode sombre */
:deep(.v-theme--dark) .app-background {
  background-color: #121212 !important;
}
:deep(.v-theme--dark) .footer-card {
  background-color: #1e1e1e !important;
}
</style>