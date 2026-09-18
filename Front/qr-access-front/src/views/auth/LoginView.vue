<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5" lg="4">
        <v-card 
          title="Connexion - QR-ACCESS Admin" 
          class="pa-4" 
          elevation="12"
          :loading="loading"
        >
          <v-card-text>
            
            <v-alert
              v-if="errorMessage"
              type="error"
              class="mb-4"
              prominent
              density="compact"
            >
              {{ errorMessage }}
            </v-alert>

            <v-form @submit.prevent="handleLogin" ref="form">
              
             <v-text-field
                v-model="nom_utilisateur" label="Nom d'utilisateur"
                required
                :rules="[v => !!v || 'Le nom d\'utilisateur est requis']"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                class="mb-3"
                ></v-text-field>

                <v-text-field
                v-model="mot_de_passe" label="Mot de passe"
                required
                :type="showPassword ? 'text' : 'password'"
                :rules="[v => !!v || 'Le mot de passe est requis']"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                variant="outlined"
                class="mb-5"
                ></v-text-field>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="loading"
              >
                Se Connecter
              </v-btn>
              
              <v-divider class="my-5"></v-divider>

              <div class="text-center">
                  <v-btn variant="text" :to="{ name: 'Home' }">
                      Retour à la Page d'Accueil
                  </v-btn>
              </div>

            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

// MODÈLES DE FORMULAIRE MIS À JOUR : Utilisation des noms de clés du backend
const nom_utilisateur = ref(''); // Anciennement 'username'
const mot_de_passe = ref('');    // Anciennement 'password'
const showPassword = ref(false);

// État de la vue
const loading = ref(false);
const errorMessage = ref(null);
const form = ref(null);

/**
 * Gère la soumission du formulaire de connexion.
 * Utilise désormais 'nom_utilisateur' et 'mot_de_passe' pour l'appel API.
 */
const handleLogin = async () => {
    errorMessage.value = null;
    
    const { valid } = await form.value.validate();
    if (!valid) {
        return;
    }

    loading.value = true;
    try {
        await authStore.login({
            // ENVOI DES CLÉS DU BACKEND
            nom_utilisateur: nom_utilisateur.value, 
            mot_de_passe: mot_de_passe.value // ENVOI DE LA CLÉ DU BACKEND
        });
        
        // La redirection est gérée dans le AuthStore en cas de succès
        
    } catch (error) {
        // L'erreur est retournée par l'API
        errorMessage.value = error || "Une erreur inattendue est survenue.";
        
    } finally {
        loading.value = false;
    }
};

// Si l'utilisateur est déjà connecté, le rediriger
if (authStore.isAuthenticated) {
    router.push({ name: 'AdminDashboard' });
}
</script>

<style scoped>
.fill-height {
    height: 100vh;
}
</style>