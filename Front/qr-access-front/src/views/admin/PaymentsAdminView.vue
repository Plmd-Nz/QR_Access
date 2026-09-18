<template>
  <v-container fluid class="py-6">
    <div class="d-flex align-center mb-6">
      <h1 class="text-h4">Gestion des Paiements</h1>
      <v-spacer></v-spacer>
      <v-btn color="success" prepend-icon="mdi-plus-circle" @click="openDialog()">
        Enregistrer un Paiement
      </v-btn>
    </div>

    <v-card elevation="4">
      <v-card-title>
        <v-text-field v-model="search" append-inner-icon="mdi-magnify" label="Rechercher un paiement..." single-line
          hide-details variant="outlined" density="compact"></v-text-field>
      </v-card-title>

      <v-alert v-if="paymentStore.error" type="error" closable class="ma-4">
        {{ paymentStore.error }}
      </v-alert>

      <v-table fixed-header height="600px" class="pa-4">
        <thead>
          <tr>
            <th>Date</th>
            <th>Étudiant (Matricule)</th>
            <th>Montant</th>
            <th>Description / Année</th>
            <th class="text-center">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredPayments" :key="item.id">
            <td>{{ formatDate(item.date_paiement) }}</td>
            <td>
              <div class="font-weight-bold">{{ item.nom_etudiant || 'Inconnu' }}</div>
              <div class="text-caption text-grey">{{ item.matricule }}</div>
            </td>
            <td class="text-success font-weight-bold">{{ formatCurrency(item.montant) }}</td>
            <td>
              {{ item.description }}
              <v-chip size="x-small" class="ml-2" color="primary">{{ item.annee_academique }}</v-chip>
            </td>
            <td class="text-center">
              <v-btn icon="mdi-pencil" variant="text" size="small" color="blue" @click="openDialog(item)"></v-btn>
              <v-btn icon="mdi-delete" variant="text" size="small" color="red" @click="confirmDelete(item.id)"></v-btn>
            </td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-dialog v-model="dialog" max-width="600px" persistent>
      <v-card :title="isEditing ? 'Modifier le Paiement' : 'Enregistrer un Nouveau Paiement'">
        <v-card-text>
          <v-form ref="paymentForm">
            <v-row>
              <v-col cols="12">
                <v-autocomplete v-model="formData.student_id" :items="paymentStore.studentsForSelection"
                  item-title="display_name" item-value="id" label="Rechercher un étudiant (Nom ou Matricule)"
                  placeholder="Tapez le nom ou le matricule..." :rules="[v => !!v || 'L\'étudiant est requis']"
                  variant="outlined" prepend-inner-icon="mdi-account-search" :loading="loadingStudents"
                  :disabled="isEditing" clearable auto-select-first no-data-text="Aucun étudiant trouvé">
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props" :title="item.raw.display_name"
                      subtitle="Sélectionner pour le paiement"></v-list-item>
                  </template>
                </v-autocomplete>
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field v-model.number="formData.montant_paye" label="Montant (USD)" type="number" prefix="$"
                  :rules="[v => v > 0 || 'Montant invalide']" variant="outlined"></v-text-field>
              </v-col>

              <v-col cols="12" md="6">
                <v-select v-model="formData.annee_academique" :items="['2023-2024', '2024-2025', '2025-2026']"
                  label="Année Académique" :rules="[v => !!v || 'Requis']" variant="outlined"></v-select>
              </v-col>

              <v-col cols="12">
                <v-select v-model="formData.description" :items="motifsPaiement" label="Motif du paiement"
                  variant="outlined" prepend-inner-icon="mdi-format-list-bulleted"></v-select>
              </v-col>

              <v-col cols="12" v-if="formData.description === 'Autre'">
                <v-text-field v-model="formData.autreMotif" label="Précisez le motif"
                  placeholder="Ex: Frais de stage, Duplicata carte..." variant="outlined" color="orange"
                  :rules="[v => !!v || 'Veuillez préciser le motif']"
                  prepend-inner-icon="mdi-pencil-plus"></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeDialog">Annuler</v-btn>
          <v-btn color="primary" variant="flat" :loading="isSaving" @click="handleSave">
            {{ isEditing ? 'Mettre à jour' : 'Enregistrer' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { usePaymentStore } from '@/stores/payment';

const paymentStore = usePaymentStore();
const search = ref('');
const dialog = ref(false);
const paymentForm = ref(null);
const isSaving = ref(false);
const isEditing = ref(false);
const currentId = ref(null);
const loadingStudents = ref(false);

// Liste des motifs prédéfinis
const motifsPaiement = [
  'Frais académique',
  'Frais de deuxième session',
  'Autre'
];


const defaultData = {
  student_id: null,
  montant_paye: 0,
  description: motifsPaiement[0], // Par défaut : Frais académique
  autreMotif: '',
  annee_academique: '2024-2025'
};

const formData = ref({ ...defaultData });

const filteredPayments = computed(() => {
  const term = search.value.toLowerCase();
  return paymentStore.payments.filter(p =>
    p.nom_etudiant?.toLowerCase().includes(term) ||
    p.matricule?.toLowerCase().includes(term) ||
    p.description?.toLowerCase().includes(term)
  );
});


const openDialog = async (item = null) => {
  if (item) {
    isEditing.value = true;
    currentId.value = item.id;
    // On remplit le formulaire avec les données existantes
    formData.value = {
      student_id: item.etudiant_id,
      montant_paye: parseFloat(item.montant),
      description: item.description,
      annee_academique: item.annee_academique
    };
  } else {
    isEditing.value = false;
    formData.value = { ...defaultData };
  }

  dialog.value = true;
  if (paymentStore.studentsForSelection.length === 0) {
    loadingStudents.value = true;
    await paymentStore.fetchStudentsForSelection();
    loadingStudents.value = false;
  }
};

const handleSave = async () => {
  const { valid } = await paymentForm.value.validate();
  if (!valid) return;

  isSaving.value = true;

  // LOGIQUE CRUCIALE : Si "Autre" est choisi, on utilise le contenu du champ texte libre
  const finalDescription = formData.value.description === 'Autre'
    ? formData.value.autreMotif
    : formData.value.description;

  const payload = {
    ...formData.value,
    description: finalDescription // On écrase avec la valeur réelle
  };

  try {
    if (isEditing.value) {
      await paymentStore.updatePayment(currentId.value, formData.value);
    } else {
      await paymentStore.createPayment(formData.value);
    }
    closeDialog();
  } catch (e) {
    console.error(e);
  } finally {
    isSaving.value = false;
  }
};

const confirmDelete = async (id) => {
  await paymentStore.deletePayment(id);
};

const closeDialog = () => {
  dialog.value = false;
  isEditing.value = false;
};

const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
const formatDate = (ds) => ds ? new Date(ds).toLocaleDateString() : 'N/A';

onMounted(() => paymentStore.fetchPayments());
</script>