<template>
  <v-container fluid class="py-6">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4">Configuration des Points d'Accès</h1>
      <v-spacer></v-spacer>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog()">
        Nouveau Point d'Accès
      </v-btn>
    </div>

    <v-row>
      <v-col v-for="point in accessStore.pointsAcces" :key="point.id" cols="12" sm="6" md="4">
        <v-card color="teal-darken-1" theme="dark" elevation="4" class="hover-card-strong" border>
          <v-card-item>
            <template v-slot:prepend>
              <v-icon size="large" :color="getTypeColor(point.type_acces)">
                {{ getTypeIcon(point.type_acces) }}
              </v-icon>
            </template>
            <v-card-title>{{ point.nom_point }}</v-card-title>
            <v-card-subtitle>{{ point.type_acces }}</v-card-subtitle>
          </v-card-item>

          <v-divider></v-divider>

          <v-card-text>
            <div class="d-flex align-center mb-2">
              <v-icon size="small" class="mr-2">mdi-account-school</v-icon>
              <span>Restriction : <strong>{{ point.promotion_nom || 'Accès Général' }}</strong></span>
            </div>
            <div class="d-flex align-center">
              <v-icon size="small" class="mr-2">mdi-clock-outline</v-icon>
              <span>Horaire : {{ point.heure_debut || '00:00' }} - {{ point.heure_fin || '23:59' }}</span>
            </div>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn icon="mdi-pencil" variant="text" color="blue" @click="openDialog(point)"></v-btn>
            <v-btn icon="mdi-delete" variant="text" color="error" @click="confirmDelete(point)"></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card :title="isEdit ? 'Modifier le Point d\'Accès' : 'Nouveau Point d\'Accès'">
        <v-card-text>
          <v-form ref="formRef">
            <v-row>
              <v-col cols="12">
                <v-text-field 
                  v-model="form.nom_point" 
                  label="Nom du Point (ex: Entrée Principale)" 
                  variant="outlined"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.type_acces"
                  :items="['CAMPUS', 'AUDITOIRE', 'SALLE_EXAMEN', 'AUTRE']"
                  label="Type d'Accès"
                  variant="outlined"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="form.promotion_id"
                  :items="academicStore.promotions"
                  item-title="nom"
                  item-value="id"
                  label="Promotion Autorisée"
                  placeholder="Laisser vide pour accès général"
                  variant="outlined"
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.heure_debut"
                  label="Heure de Début"
                  type="time"
                  variant="outlined"
                  hint="Format HH:MM"
                  persistent-hint
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.heure_fin"
                  label="Heure de Fin"
                  type="time"
                  variant="outlined"
                  hint="Format HH:MM"
                  persistent-hint
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="dialog = false">Annuler</v-btn>
          <v-btn color="primary" variant="flat" :loading="saving" @click="handleSave">Enregistrer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

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

<script setup>
import { ref, onMounted } from 'vue';
import { useAccessStore } from '@/stores/access';
import { useAcademicStore } from '@/stores/academic';

const accessStore = useAccessStore();
const academicStore = useAcademicStore();

const dialog = ref(false);
const isEdit = ref(false);
const saving = ref(false);
const currentId = ref(null);

const form = ref({
  nom_point: '',
  type_acces: 'CAMPUS',
  promotion_id: null,
  heure_debut: '08:00',
  heure_fin: '17:00'
});

const openDialog = (item = null) => {
  isEdit.value = !!item;
  if (item) {
    currentId.value = item.id;
    form.value = { ...item };
  } else {
    form.value = { nom_point: '', type_acces: 'CAMPUS', promotion_id: null, heure_debut: '08:00', heure_fin: '17:00' };
  }
  dialog.value = true;
};

const handleSave = async () => {
  saving.value = true;
  try {
    if (isEdit.value) {
      await accessStore.updatePoint(currentId.value, form.value);
    } else {
      await accessStore.addPoint(form.value);
    }
    dialog.value = false;
  } catch (e) {
    alert(e.response?.data?.message || "Erreur lors de l'enregistrement");
  } finally {
    saving.value = false;
  }
};

const confirmDelete = async (item) => {
  if (confirm(`Supprimer le point d'accès ${item.nom_point} ?`)) {
    try {
      await accessStore.deletePoint(item.id);
    } catch (e) {
      alert(e.response?.data?.detail || "Impossible de supprimer ce point.");
    }
  }
};

const getTypeIcon = (type) => {
  const icons = { 
    'Principal': 'mdi-gate', 
    'Cours': 'mdi-lecture-hall', 
    'Examen': 'mdi-file-document-edit', 
    'Laboratoire': 'mdi-flask' 
  };
  return icons[type] || 'mdi-map-marker';
};

const getTypeColor = (type) => {
  const colors = { 
    'Principal': 'green', 
    'Cours': 'blue', 
    'Examen': 'orange', 
    'Laboratoire': 'purple' 
  };
  return colors[type] || 'grey';
};

onMounted(() => {
  accessStore.fetchPoints();
  academicStore.fetchAll(); // On charge les promos pour le sélecteur
});
</script>