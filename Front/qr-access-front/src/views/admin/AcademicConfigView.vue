<template>
  <v-container fluid class="py-6">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4 font-weight-bold">Configuration de la Structure</h1>
    </div>

    <v-card variant="flat">
      <v-tabs v-model="activeTab" bg-color="transparent" color="primary" class="border-b">
        <v-tab value="facultes" class="text-none">
          <v-icon start icon="mdi-domain"></v-icon>
          Facultés ({{ academicStore.facultes.length }})
        </v-tab>
        <v-tab value="promotions" class="text-none">
          <v-icon start icon="mdi-school"></v-icon>
          Promotions ({{ academicStore.promotions.length }})
        </v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="pt-6">
        <v-window-item value="facultes">
          <div class="d-flex align-center mb-6 px-4">
            <div class="text-subtitle-1 text-grey-darken-1">Liste des établissements</div>
            <v-spacer></v-spacer>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openFaculteDialog()" elevation="3">Nouvelle Faculté</v-btn>
          </div>
          
          <v-row class="px-4">
            <v-col v-for="f in sortedFacultes" :key="f.id" cols="12" sm="6" md="4">
              <v-card color="primary" theme="dark" elevation="4" class="rounded-lg hover-card-strong">
                <v-card-item>
                  <template v-slot:prepend>
                    <v-avatar color="grey-lighten-3" rounded size="45">
                      <span class="primary font-weight-black text-caption">{{ f.code_court }}</span>
                    </v-avatar>
                  </template>
                  <div class="d-flex justify-space-between align-center w-100">
                    <v-card-title class="text-body-1 font-weight-black">{{ f.nom }}</v-card-title>
                    <v-icon icon="mdi-domain" size="24" opacity="0.5"></v-icon>
                  </div>
                </v-card-item>

                <v-divider class="mx-4 border-opacity-25" color="white"></v-divider>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn icon="mdi-pencil" variant="text" size="small" @click="openFaculteDialog(f)"></v-btn>
                  <v-btn icon="mdi-delete" variant="text" size="small" color="white" @click="handleDeleteFaculte(f)"></v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <v-window-item value="promotions">
          <div class="d-flex align-center mb-6 px-4">
            <div class="text-subtitle-1 text-grey-darken-1">Groupes d'étudiants par niveau</div>
            <v-spacer></v-spacer>
            <v-btn color="teal-darken-3" prepend-icon="mdi-plus" @click="openPromoDialog()" elevation="3">Nouvelle Promotion</v-btn>
          </div>
          
          <v-row class="px-4">
            <v-col v-for="p in sortedPromotions" :key="p.id" cols="12" sm="6" md="4">
              <v-card color="teal-darken-1" theme="dark" elevation="4" class="rounded-lg hover-card-strong">
                <v-card-text>
                  <div class="d-flex justify-space-between align-start mb-2">
                    <div class="text-h6 font-weight-black">{{ p.nom }}</div>
                    <v-chip size="x-small" color="white" text-color="teal-darken-3" variant="flat" class="font-weight-bold">
                      {{ p.faculte_nom }}
                    </v-chip>
                  </div>
                  <div class="text-body-2 opacity-90">
                    <v-icon icon="mdi-book-education" size="16" class="me-1"></v-icon>
                    Filière: {{ p.filiere || 'Générale' }}
                  </div>
                </v-card-text>

                <v-divider class="border-opacity-25" color="white"></v-divider>

                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn icon="mdi-pencil" variant="text" size="small" @click="openPromoDialog(p)"></v-btn>
                  <v-btn icon="mdi-delete" variant="text" size="small" color="white" @click="handleDeletePromo(p)"></v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>
      </v-window>
    </v-card>

    <v-dialog v-model="facDialog" max-width="500px">
      <v-card :title="isEdit ? 'Modifier Faculté' : 'Nouvelle Faculté'">
        <v-card-text>
          <v-text-field v-model="facForm.nom" label="Nom complet" variant="outlined"></v-text-field>
          <v-text-field v-model="facForm.code_court" label="Code Court (ex: INF)" variant="outlined"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="facDialog = false">Annuler</v-btn>
          <v-btn color="primary" variant="flat" @click="saveFaculte">Enregistrer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="promoDialog" max-width="500px">
      <v-card :title="isEdit ? 'Modifier Promotion' : 'Nouvelle Promotion'">
        <v-card-text>
          <v-select 
            v-model="promoForm.faculte_id" 
            :items="academicStore.facultes" 
            item-title="nom" 
            item-value="id" 
            label="Sélectionner la Faculté" 
            variant="outlined"
          ></v-select>
          <v-text-field v-model="promoForm.nom" label="Nom de la Promotion (ex: L1 LMD)" variant="outlined"></v-text-field>
          <v-text-field v-model="promoForm.filiere" label="Filière" variant="outlined"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="promoDialog = false">Annuler</v-btn>
          <v-btn color="primary" variant="flat" @click="savePromotion">Enregistrer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAcademicStore } from '@/stores/academic';

const academicStore = useAcademicStore();

// Logique de tri alphabétique
const sortedFacultes = computed(() => {
  return [...academicStore.facultes].sort((a, b) => a.nom.localeCompare(b.nom));
});

const sortedPromotions = computed(() => {
  return [...academicStore.promotions].sort((a, b) => a.nom.localeCompare(b.nom));
});

const activeTab = ref('facultes');
const facDialog = ref(false);
const promoDialog = ref(false);
const isEdit = ref(false);
const currentId = ref(null);

const facForm = ref({ nom: '', code_court: '' });
const promoForm = ref({ nom: '', filiere: '', faculte_id: null });

const openFaculteDialog = (item = null) => {
  isEdit.value = !!item;
  currentId.value = item ? item.id : null;
  facForm.value = item ? { ...item } : { nom: '', code_court: '' };
  facDialog.value = true;
};

const openPromoDialog = (item = null) => {
  isEdit.value = !!item;
  currentId.value = item ? item.id : null;
  promoForm.value = item ? { ...item } : { nom: '', filiere: '', faculte_id: null };
  promoDialog.value = true;
};

const saveFaculte = async () => {
  try {
    if (isEdit.value) await academicStore.updateFaculte(currentId.value, facForm.value);
    else await academicStore.addFaculte(facForm.value);
    facDialog.value = false;
  } catch (e) { alert(e.response?.data?.message || "Erreur"); }
};

const savePromotion = async () => {
  try {
    if (isEdit.value) await academicStore.updatePromotion(currentId.value, promoForm.value);
    else await academicStore.addPromotion(promoForm.value);
    promoDialog.value = false;
  } catch (e) { alert(e.response?.data?.message || "Erreur"); }
};

const handleDeleteFaculte = async (f) => {
  if (confirm(`Supprimer la faculté ${f.nom} ?`)) {
    try { await academicStore.deleteFaculte(f.id); } 
    catch (e) { alert(e.response?.data?.detail || "Erreur de suppression"); }
  }
};

const handleDeletePromo = async (p) => {
  if (confirm(`Supprimer la promotion ${p.nom} ?`)) {
    try { await academicStore.deletePromotion(p.id); }
    catch (e) { alert(e.reponse?.data?.detail || "Cette promotion est encore liée à des étudiants ou des points d'accès. Veuillez supprimer ou réaffecter les entités liées avant de supprimer cette promotion."); }
  }
};

onMounted(() => academicStore.fetchAll());
</script>

<style scoped>
.hover-card-strong {
  transition: all 0.3s ease;
  cursor: default;
}
.hover-card-strong:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.3) !important;
  filter: brightness(1.15);
}
</style>