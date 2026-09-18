// src/plugins/vuetify.js

// Importations standard
import 'vuetify/styles'; 
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import '@mdi/font/css/materialdesignicons.css'; // Importation des icônes MDI

// --- Définition des Thèmes ---
const lightTheme = {
  dark: false,
  colors: {
    background: '#F0F2F5', // Gris très clair pour le fond
    surface: '#FFFFFF',    // Blanc pour les cartes et surfaces
    primary: '#1976D2',    // Bleu principal (standard Vuetify)
    secondary: '#424242',  // Gris foncé
    success: '#4CAF50',
    error: '#FF5252',
    warning: '#FFC107',
  }
};

const darkTheme = {
  dark: true,
  colors: {
    background: '#121212', // Noir (mat) pour le fond
    surface: '#1E1E1E',    // Gris foncé pour les cartes
    primary: '#42A5F5',    // Bleu plus clair pour le contraste
    secondary: '#BDBDBD',
    success: '#66BB6A',
    error: '#EF5350',
    warning: '#FFD54F',
  }
};


// --- Création de l'instance Vuetify ---
const vuetify = createVuetify({
  components,
  directives,
  // Configuration des icônes
  icons: {
    default: 'mdi',
  },
  // Configuration des thèmes
  theme: {
    defaultTheme: 'lightTheme',
    themes: {
      lightTheme,
      darkTheme,
    },
  },
});

export default vuetify;