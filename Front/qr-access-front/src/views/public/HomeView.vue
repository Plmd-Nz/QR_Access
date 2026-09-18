<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center" class="text-center">
      <v-col cols="12" md="12">
        
        <h1 class="text-h2 font-weight-bold mb-4" :class="{'text-primary': !theme.global.current.value.dark}">
          QR-ACCESS : Système de Gestion des Accès et des Présences
        </h1>
        
        <p class="text-h6 mb-8 text-grey-darken-1">
          Solution numérique pour le contrôle d'accès sécurisé et le suivi des paiements universitaires via QR Codes.
        </p>
        
        <v-row justify="center" class="mb-10">
          <v-col cols="12" sm="4">
            <v-icon size="64" color="success">mdi-check-decagram</v-icon>
            <h3 class="text-h5 mt-2">Accès Sécurisé</h3>
            <p>Validation instantanée des droits d'accès.</p>
          </v-col>
          <v-col cols="12" sm="4">
            <v-icon size="64" color="info">mdi-qrcode</v-icon>
            <h3 class="text-h5 mt-2">Technologie QR</h3>
            <p>Scan rapide et fiable pour l'enregistrement.</p>
          </v-col>
          <v-col cols="12" sm="4">
            <v-icon size="64" color="warning">mdi-database</v-icon>
            <h3 class="text-h5 mt-2">Rapports Temps Réel</h3>
            <p>Suivi et gestion administrative simplifiés.</p>
          </v-col>
        </v-row>

        <v-row justify="center">
          
          <v-col cols="12" sm="6">
            <v-card class="pa-6 bg-grey-lighten-4" elevation="8" hover :to="{ name: 'AcessChoix' }">
              <v-icon size="40" color="primary" class="mb-3">mdi-wrench</v-icon>
              <h4 class="text-h5 mb-2">Configurer un Terminal</h4>
              <p class="text-subtitle-1 text-grey-darken-1">
                Définir le lieu et le type de scan pour un nouveau point d'accès.
              </p>
              <v-btn color="primary" variant="flat" class="mt-4">
                Démarrer la Configuration
              </v-btn>
            </v-card>
          </v-col>
          
          <v-col cols="12" sm="6">
            <v-card class="pa-6 bg-grey-lighten-4" elevation="8" hover :to="{ name: 'Login' }">
              <v-icon size="40" color="secondary" class="mb-3">mdi-lock</v-icon>
              <h4 class="text-h5 mb-2">Accès Administration</h4>
              <p class="text-subtitle-1 text-grey-darken-1">
                Gérer les étudiants, les paiements et les rapports du système.
              </p>
              <v-btn color="secondary" variant="outlined" class="mt-4">
                Se Connecter
              </v-btn>
            </v-card>
          </v-col>
        </v-row>
        
        
  <div class="d-flex justify-center bg-primary rounded-pill mt-4 px-4 py-1 mx-auto" style="max-width: fit-content;">
    <p class="ma-0 text-caption text-white">
      &copy; Plmd_Nz - {{ new Date().getFullYear() }} - Tous droits réservés.
    </p>
  </div>


      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { useTheme } from 'vuetify';

const theme = useTheme();

// Utilise `fill-height` pour centrer le contenu verticalement.
</script>

<style scoped>
.fill-height {
    min-height: 100vh;
}
</style>