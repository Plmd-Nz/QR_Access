<template>
  <v-container fluid class="py-6">
    <div class="d-flex align-center mb-6">
      <div>
        <h1 class="text-h4 font-weight-bold">Portail Académique</h1>
        <v-breadcrumbs :items="navBreadcrumbs" class="pa-0 mt-2">
          <template v-slot:divider>
            <v-icon icon="mdi-chevron-right"></v-icon>
          </template>
        </v-breadcrumbs>
      </div>
      <v-spacer></v-spacer>
      <v-btn color="success" prepend-icon="mdi-plus-circle" elevation="2" @click="openDialog(null)">
        Nouvelle Inscription
      </v-btn>
    </div>

    <v-card elevation="2" class="mb-6">
      <v-card-text>
        <v-text-field v-model="search" append-inner-icon="mdi-magnify" 
          label="Rechercher un étudiant (Nom ou Matricule)..."
          variant="outlined" density="comfortable" hide-details clearable>
        </v-text-field>
      </v-card-text>
    </v-card>

    <v-alert v-if="studentStore.error || academicStore.error" type="error" closable class="mb-4">
      {{ studentStore.error || academicStore.error }}
    </v-alert>

    <v-row v-if="currentStep === 'faculties'">
      <v-col v-for="fac in academicStore.facultes" :key="fac.id" cols="12" sm="6" md="4" lg="3">
        <v-card @click="goToPromotions(fac)" hover class="text-center pa-6" border elevation="2">
          <v-avatar color="primary-lighten-4" size="70" class="mb-4">
            <v-icon size="35" color="primary">mdi-school</v-icon>
          </v-avatar>
          <h3 class="text-h6 font-weight-bold text-uppercase">{{ fac.nom }}</h3>
          <div class="text-caption text-grey mt-2">Cliquez pour explorer</div>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-else-if="currentStep === 'promotions'">
      <v-col v-for="promo in navigationPromotions" :key="promo.id" cols="12" sm="6" md="3">
        <v-card @click="goToStudents(promo)" hover class="pa-5 text-center border-s-xl" 
          style="border-inline-start-color: #003366 !important">
          <h3 class="text-h5 font-weight-black">{{ promo.nom }}</h3>
          <v-chip size="x-small" class="mt-2">Promotion active</v-chip>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-else-if="currentStep === 'students'">
      <v-col v-for="item in filteredStudents" :key="item.id" cols="12" sm="6" md="4" lg="3">
        <v-card elevation="3" class="rounded-lg overflow-hidden">
          <v-sheet color="#003366" height="50"></v-sheet>
          <div class="px-4" style="margin-top: -30px">
            <v-avatar size="75" class="elevation-4" style="border: 3px solid white">
              <v-img :src="getImageUrl(item.photo_path)" cover>
                <template v-slot:placeholder><v-icon size="40">mdi-account</v-icon></template>
              </v-img>
            </v-avatar>
          </div>

          <v-card-text class="pt-2">
            <div class="font-weight-bold text-h6">{{ item.nom }} {{ item.postnom }}</div>
            <div class="text-subtitle-2 text-primary">{{ item.prenom }}</div>
            <v-divider class="my-3"></v-divider>
            <div class="text-caption mb-1">MATRICULE : <strong>{{ item.matricule }}</strong></div>
            <div class="d-flex align-center text-caption">
              QR CODE : 
              <v-icon :color="item.qr_code_cle ? 'success' : 'warning'" size="small" class="ml-2">
                {{ item.qr_code_cle ? 'mdi-check-circle' : 'mdi-clock' }}
              </v-icon>
            </div>
          </v-card-text>

          <v-divider></v-divider>

          <v-card-actions class="bg-grey-lighten-4">
            <v-btn icon="mdi-pencil" variant="text" size="small" color="primary" @click="openDialog(item)"></v-btn>
            <v-btn icon="mdi-delete" variant="text" size="small" color="error" @click="deleteItem(item)"></v-btn>
            <v-spacer></v-spacer>
            <v-btn variant="flat" size="small" color="primary" prepend-icon="mdi-card-account-details" @click="viewCard(item)">
              Carte
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="800px" persistent>
      <v-card :title="isEditing ? 'Modifier l\'Étudiant' : 'Nouvelle Inscription'">
        <v-card-text>
          <v-form ref="studentForm">
            <v-row>
              <v-col cols="12" md="4"><v-text-field v-model="editedItem.nom" label="Nom" variant="outlined"></v-text-field></v-col>
              <v-col cols="12" md="4"><v-text-field v-model="editedItem.postnom" label="Postnom" variant="outlined"></v-text-field></v-col>
              <v-col cols="12" md="4"><v-text-field v-model="editedItem.prenom" label="Prénom" variant="outlined"></v-text-field></v-col>
              <v-col cols="12" md="6">
                <v-select v-model="editedItem.faculte_id" :items="academicStore.facultes" item-title="nom" item-value="id" label="Faculté" variant="outlined" @update:model-value="editedItem.promotion_id = null"></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select v-model="editedItem.promotion_id" :items="dialogPromotions" item-title="nom" item-value="id" label="Promotion" variant="outlined" :disabled="!editedItem.faculte_id"></v-select>
              </v-col>
              <v-col cols="12" md="4"><v-text-field v-model="editedItem.email" label="E-mail pour l'evoie de la carte" variant="outlined"></v-text-field></v-col>
              <v-col cols="12" v-if="!isEditing">
                <v-file-input v-model="selectedFile" label="Photo" variant="outlined" prepend-icon="mdi-camera" @change="onFileChange"></v-file-input>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="closeDialog">Annuler</v-btn>
          <v-btn color="primary" :loading="isSaving" @click="handleSave">Enregistrer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showCardDialog" max-width="550px">
      <v-card class="pa-4 text-center">
        <v-card-title>Aperçu de la Carte</v-card-title>
        <v-img :src="generatedCardUrl" class="my-4" border rounded elevation="2"></v-img>
        <v-card-actions>
          <v-btn variant="outlined" @click="showCardDialog = false">Fermer</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" prepend-icon="mdi-printer" @click="printCard">Imprimer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card title="Attention">
        <v-card-text>Supprimer l'étudiant {{ itemToDelete?.nom }} ?</v-card-text>
        <v-card-actions>
          <v-btn @click="deleteDialog = false">Annuler</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="error" @click="confirmDelete" :loading="isSaving">Confirmer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useStudentStore } from '@/stores/student';
import { useAcademicStore } from '@/stores/academic';

const studentStore = useStudentStore();
const academicStore = useAcademicStore();

// --- ETATS DE NAVIGATION ---
const currentStep = ref('faculties');
const selectedFac = ref(null);
const selectedPromo = ref(null);

// --- ETATS UI ---
const search = ref('');
const dialog = ref(false);
const deleteDialog = ref(false);
const showCardDialog = ref(false);
const isSaving = ref(false);
const isEditing = ref(false);
const studentForm = ref(null);
const selectedFile = ref(null);
const generatedCardUrl = ref('');
const itemToDelete = ref(null);

const defaultItem = { nom: '', postnom: '', prenom: '', genre: 'M', email: '', faculte_id: null, promotion_id: null };
const editedItem = ref({ ...defaultItem });

// --- LOGIQUE DE NAVIGATION ---
const goToPromotions = (fac) => {
  selectedFac.value = fac;
  currentStep.value = 'promotions';
};

const goToStudents = (promo) => {
  selectedPromo.value = promo;
  currentStep.value = 'students';
};

const navBreadcrumbs = computed(() => {
  const steps = [{ title: 'Facultés', disabled: false, onClick: () => resetNav() }];
  if (selectedFac.value) {
    steps.push({ title: selectedFac.value.nom, disabled: false, onClick: () => { currentStep.value = 'promotions'; selectedPromo.value = null; } });
  }
  if (selectedPromo.value) {
    steps.push({ title: selectedPromo.value.nom, disabled: true });
  }
  return steps;
});

const resetNav = () => {
  currentStep.value = 'faculties';
  selectedFac.value = null;
  selectedPromo.value = null;
};

// --- FILTRAGES ---
const navigationPromotions = computed(() => {
  if (!selectedFac.value) return [];
  return academicStore.promotions.filter(p => p.faculte_id === selectedFac.value.id);
});

const dialogPromotions = computed(() => {
  if (!editedItem.value.faculte_id) return [];
  return academicStore.promotions.filter(p => p.faculte_id === editedItem.value.faculte_id);
});

const filteredStudents = computed(() => {
  let list = studentStore.students;
  if (selectedPromo.value) {
    list = list.filter(s => s.promotion_id === selectedPromo.value.id);
  }
  const term = search.value.toLowerCase();
  return list.filter(s => s.nom.toLowerCase().includes(term) || s.matricule.toLowerCase().includes(term));
});

// --- ACTIONS ---
const onFileChange = (e) => {
  const file = e.target.files[0];
  if (file) selectedFile.value = file;
};

const openDialog = (item = null) => {
  if (item) {
    isEditing.value = true;
    editedItem.value = { ...item };
  } else {
    isEditing.value = false;
    editedItem.value = { ...defaultItem };
    if (selectedFac.value) editedItem.value.faculte_id = selectedFac.value.id;
    if (selectedPromo.value) editedItem.value.promotion_id = selectedPromo.value.id;
  }
  dialog.value = true;
};

const closeDialog = () => { dialog.value = false; isEditing.value = false; };

const handleSave = async () => {
  const { valid } = await studentForm.value.validate();
  if (!valid) return;
  isSaving.value = true;
  try {
    if (isEditing.value) {
      await studentStore.updateStudent(editedItem.value.matricule, editedItem.value);
      closeDialog();
    } else {
      const fd = new FormData();
      Object.keys(editedItem.value).forEach(k => fd.append(k, editedItem.value[k]));
      if (selectedFile.value) fd.append('photo', selectedFile.value);
      
      const response = await studentStore.createStudent(fd);
         // Vérification du chemin de réponse (souvent response.data.data sous Axios/Pinia)
    const responseData = response?.data?.data || response?.data;

    if (responseData && responseData.card_url) {
      // On construit l'URL complète si nécessaire (ajuster selon ton backend)
      const baseUrl = "http://localhost:5000/";
      generatedCardUrl.value = responseData.card_url.startsWith('http') 
      ? responseData.card_url 
      : baseUrl + responseData.card_url;
      
      closeDialog();
      showCardDialog.value = true;
    } else {
      // Si l'inscription réussit mais la carte n'est pas renvoyée
      closeDialog();
      alert("Inscription réussie (sans génération de carte).");
    }

    }
  } catch (e) { alert(e); } finally { isSaving.value = false; }
};

const viewCard = (item) => {
  const safeMatricule = item.matricule.replace(/\//g, '_');
  generatedCardUrl.value = `http://localhost:5000/static/photos/card_${safeMatricule}.png`;
  showCardDialog.value = true;
};

const printCard = () => {
  const win = window.open('', '_blank');
  win.document.write(`<html><body style="margin:0;display:flex;justify-content:center"><img src="${generatedCardUrl.value}" style="max-width:100%" onload="window.print();window.close()"></body></html>`);
  win.document.close();
};

const deleteItem = (item) => { itemToDelete.value = item; deleteDialog.value = true; };
const confirmDelete = async () => {
  isSaving.value = true;
  try {
    await studentStore.deleteStudent(itemToDelete.value.matricule);
    deleteDialog.value = false;
  } catch (e) { alert(e); } finally { isSaving.value = false; }
};

const getImageUrl = (path) => path ? `http://localhost:5000/${path}` : '';

onMounted(async () => {
  await academicStore.fetchAll();
  await studentStore.fetchStudents();
});
</script>