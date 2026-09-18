<template>
  <v-container fluid class="pa-0 fill-height scan-interface bg-grey-lighten-4">
    <v-row v-if="!scanStore.isConfigured" align="center" justify="center" class="text-center fill-height bg-grey-lighten-4">
      <v-col cols="12">
        <v-icon size="100" color="warning" class="mb-4">mdi-cog-off</v-icon>
        <h2 class="text-h4 mb-4">Terminal Non Configuré</h2>
        <v-btn color="primary" size="x-large" rounded to="/choix">
          Choisir un Point d'Accès
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-else  justify="center" class="fill-height ma-0">
      
      <v-col cols="12" md="8" class="pa-0 d-flex flex-column align-center justify-center">
        
        <v-alert
          :type="scanStatus.type"
          :icon="scanStatus.icon"
          prominent
          class="scan-message-card mb-6 shadow-lg"
          elevation="10"
        >
          <div class="text-h4 font-weight-black mb-2 text-uppercase">{{ scanStatus.title }}</div>
          <div class="text-h5">{{ scanStatus.message }}</div>
        </v-alert>

        <div class="qr-wrapper">
          <div v-if="isCodeDetected" class="scanner-laser"></div>
          
          <qrcode-stream 
            @detect="onDetect" 
            :track="paintOutline"
            class="qr-video"
          />
        </div>
        
        <v-chip class="mt-6 pa-6" color="white" variant="flat" elevation="2">
          <v-icon start icon="mdi-map-marker-radius" color="primary"></v-icon>
          <span class="text-h6 font-weight-bold text-primary">POSTE : {{ scanStore.currentLocationTitle }}</span>
          <v-divider vertical class="mx-4"></v-divider>
          <v-btn size="small" variant="text" color="primary" to="/choix">Changer</v-btn>
        </v-chip>
      </v-col>

      <v-col cols="12" md="4" class="right-panel pa-4 d-flex flex-column">
        
        <v-card v-if="lastScan.etudiant" elevation="4" rounded="xl" class="mb-4 student-detail-card">
          <v-card-text class="pa-6">
            <div class="d-flex align-center flex-column">
              <v-avatar size="150" border class="mb-4 elevation-2">
                <v-img v-if="lastScan.etudiant.photo_path" :src="lastScan.etudiant.photo_path" cover></v-img>
                <v-icon v-else size="100" icon="mdi-account"></v-icon>
              </v-avatar>
              <h2 class="text-h4 font-weight-bold text-center mb-1">{{ lastScan.etudiant.nom_complet }}</h2>
              <v-chip color="primary" variant="tonal" class="mb-4 font-weight-bold">{{ lastScan.etudiant.matricule }}</v-chip>
              
              <v-list width="100%" density="compact">
                <v-list-item prepend-icon="mdi-school" :title="lastScan.etudiant.promotion" subtitle="Promotion"></v-list-item>
              </v-list>
            </div>
          </v-card-text>
        </v-card>

        <div class="flex-grow-1 overflow-hidden d-flex flex-column">
          <div class="d-flex justify-space-between align-center mb-4">
            <h3 class="text-h6 font-weight-bold text-grey-darken-3">Passages récents</h3>
            <v-badge v-if="recentScans" :content="recentScans.length" color="primary" inline></v-badge>
          </div>

          <v-list class="history-list flex-grow-1 overflow-y-auto bg-transparent">
            <v-hover v-for="item in recentScans" :key="item.id" v-slot="{ isHovering, props }">
              <v-list-item
                v-bind="props"
                :elevation="isHovering ? 4 : 0"
                class="mb-3 rounded-lg history-item"
                :class="item.statut === 'autorise' ? 'border-left-success' : 'border-left-error'"
              >
                <template v-slot:prepend>
                  <v-avatar size="45" :color="item.statut === 'autorise' ? 'success-lighten-4' : 'error-lighten-4'">
                    <v-icon :color="item.statut === 'autorise' ? 'success' : 'error'">
                      {{ item.statut === 'autorise' ? 'mdi-check' : 'mdi-alert' }}
                    </v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-bold">{{ item.nom_complet }}</v-list-item-title>
                <v-list-item-subtitle>{{ formatTime(item.timestamp) }}</v-list-item-subtitle>

                <template v-slot:append>
                  <div class="text-right">
                    <div :class="item.statut === 'autorise' ? 'text-success' : 'text-error'" class="text-caption font-weight-black">
                      {{ item.statut.toUpperCase() }}
                    </div>
                  </div>
                </template>
              </v-list-item>
            </v-hover>
          </v-list>
          
          <div v-if="!recentScans || recentScans.length === 0" class="text-center py-10 text-grey">
            <v-icon size="50" icon="mdi-tray-blank" class="mb-2"></v-icon>
            <p>Aucun passage enregistré aujourd'hui</p>
          </div>
        </div>
      </v-col>
       <v-col class="bg-primary py-2"> <div class="d-flex justify-center">
            <p class="mt-0 text-caption">
            &copy; Plmd_Nz - {{ new Date().getFullYear() }} - Tous droits réservés.
            </p>
        </div></v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { QrcodeStream } from 'vue-qrcode-reader';
import { useScanStore } from '@/stores/scan';
import api from '@/services/api';

const scanStore = useScanStore();
const recentScans = ref([]);
const scanInProgress = ref(false);
const isCodeDetected = ref(false); // État pour l'animation laser
let refreshTimer = null;
let detectionTimeout = null;

const lastScan = ref({
    statut_acces: 'idle',
    message: 'En attente d\'un badge...',
    etudiant: null
});

// --- COULEURS DYNAMIQUES ---
const backgroundStatusColor = computed(() => {
    if (lastScan.value.statut_acces === 'success') return '#1B5E20';
    if (lastScan.value.statut_acces === 'error') return '#B71C1C';
    return '#f5f5f5';
});

const scanStatus = computed(() => {
    if (lastScan.value.statut_acces === 'success') return { type: 'success', icon: 'mdi-check-decagram', title: 'Entrée Autorisée', message: lastScan.value.message };
    if (lastScan.value.statut_acces === 'error') return { type: 'error', icon: 'mdi-shield-alert', title: 'Accès Refusé', message: lastScan.value.message };
    return { type: 'info', icon: 'mdi-qrcode-scan', title: 'Prêt', message: 'Veuillez présenter votre carte' };
});

// --- LOGIQUE API ---
const onDetect = (detectedCodes) => {
    // Activer l'animation laser
    isCodeDetected.value = true;
    
    // Réinitialiser le laser après 500ms s'il n'y a plus de détection
    clearTimeout(detectionTimeout);
    detectionTimeout = setTimeout(() => {
        isCodeDetected.value = false;
    }, 500);

    if (scanInProgress.value || !scanStore.isConfigured) return;
    
    const code = detectedCodes[0].rawValue;
    if (code) processScan(code);
};

const processScan = async (qrCode) => {
    scanInProgress.value = true;
    try {
        const response = await api.post('/scan/', {
            qr_code_cle: qrCode,
            point_acces_id: scanStore.terminalConfig.point_acces_id 
        });

        // CAS SUCCÈS (HTTP 200)
        const res = response.data;
        lastScan.value.statut_acces = 'success';
        lastScan.value.message = res.data?.message || "Accès autorisé";
        lastScan.value.etudiant = res.data;

    } catch (error) {
        // CAS ERREUR (HTTP 403, 500, etc.)
        lastScan.value.statut_acces = 'error';
        
        // C'est ici qu'on récupère le message même si c'est une 403
        const errData = error.response?.data;
        
        // On cherche le message dans data.message (structure Flask) ou à la racine du JSON
        lastScan.value.message = errData?.data?.message || errData?.message || "Accès Refusé (Règle de sécurité)";
        
        // Optionnel : on récupère les infos de l'étudiant si elles sont présentes malgré le refus
        lastScan.value.etudiant = errData?.data || null;
        
        console.warn("Détails du refus:", lastScan.value.message);
    } finally {
        await fetchHistory();
        setTimeout(() => {
            // On ne repasse en idle que si un autre scan n'a pas démarré
            if (scanInProgress.value) {
                lastScan.value.statut_acces = 'idle';
                scanInProgress.value = false;
            }
        }, 4000); 
    }
};

const fetchHistory = async () => {
    if (!scanStore.isConfigured) return;
    try {
        const response = await api.get(`/scan/recent?point_acces_id=${scanStore.terminalConfig.point_acces_id}`);
        recentScans.value = response.data?.history || [];
    } catch (e) {
        console.error("Erreur historique:", e);
        recentScans.value = []; 
    }
};

const formatTime = (ts) => {
    if (!ts) return "--:--";
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// --- CYCLE DE VIE ---
onMounted(() => {
    scanStore.loadConfiguration();
    if (scanStore.isConfigured) {
        fetchHistory();
        refreshTimer = setInterval(fetchHistory, 10000);
    }
});

onUnmounted(() => {
    if (refreshTimer) clearInterval(refreshTimer);
    if (detectionTimeout) clearTimeout(detectionTimeout);
});

const paintOutline = (detectedCodes, ctx) => {
    for (const detected of detectedCodes) {
        const [first, ...others] = detected.cornerPoints;
        ctx.strokeStyle = "#00E676";
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(first.x, first.y);
        others.forEach(({x, y}) => ctx.lineTo(x, y));
        ctx.lineTo(first.x, first.y);
        ctx.stroke();
    }
};
</script>

<style scoped>
.scan-interface { transition: background 0.4s ease; }
.qr-wrapper {
  position: relative;
  width: 400px;
  max-width: 90vw;
  height: 400px;
  border: 8px solid white;
  border-radius: 40px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
}
.scanner-laser {
  position: absolute;
  top: 0; left: 0; right: 0; height: 4px;
  background: #00E676;
  z-index: 10;
  box-shadow: 0 0 15px #00E676;
  animation: scanning 1.5s infinite linear;
}
@keyframes scanning {
  0% { top: 0%; }
  50% { top: 100%; }
  100% { top: 0%; }
}
.right-panel { background: #ffffff !important; border-left: 1px solid #ddd; }
.history-item { border-left: 6px solid transparent; transition: all 0.2s; }
.border-left-success { border-left-color: #4CAF50 !important; background: #E8F5E9 !important; }
.border-left-error { border-left-color: #F44336 !important; background: #FFEBEE !important; }
.scan-message-card { width: 90%; max-width: 600px; border-radius: 20px !important; }
</style>