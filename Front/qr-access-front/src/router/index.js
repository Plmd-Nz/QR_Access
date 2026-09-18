// src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Importation des vues principales (que nous allons créer)
import HomeView from '@/views/public/HomeView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import ScanConfigView from '@/views/admin/ScanConfigView.vue'
import ScanInterfaceView from '@/views/scan/ScanInterfaceView.vue'
import DashboardView from '@/views/admin/DashboardView.vue'
import AcademicConfigView from "@/views/admin/AcademicConfigView.vue"
import AcessChoixView from '@/views/scan/AcessChoixView.vue'

// Vues d'administration détaillées
import StudentsAdminView from '@/views/admin/StudentsAdminView.vue'
import PaymentsAdminView from '@/views/admin/PaymentsAdminView.vue'
import ReportsAdminView from '@/views/admin/ReportsAdminView.vue'
import NotFoundView from '@/views/utility/NotFoundView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // =======================================================
    // 1. ZONES PUBLIQUES (Layout simple/sans authentification)
    // =======================================================
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      children: [
        {
          path: '/',
          name: 'ScanInterface',
          component: ScanInterfaceView, // Interface de Scan Temps Réel
          meta: { requiresAuth: false } // Rendu public
        },
        {
          path: '/Accueil',
          name: 'Home',
          component: HomeView // Page d'accueil/vitrine (QR-ACCESS)
        },
        {
          path: '/Choix',
          name: 'AcessChoix',
          component: AcessChoixView
        },

      ]
    },

    {
      path: '/login',
      name: 'Login',
      component: LoginView // Connexion Administrateur
    },

    // =======================================================
    // 2. ZONE CRITIQUE (Scan/Configuration)
    // =======================================================

    // =======================================================
    // 3. ZONE SÉCURISÉE (Administration)
    // =======================================================
    {
      path: '/admin',
      component: () => import('@/layouts/AdminLayout.vue'), // Layout avec barre de navigation statique
      meta: { requiresAuth: true }, // Toutes les sous-routes exigent l'authentification
      children: [
        {
          path: '',
          name: 'AdminDashboard',
          component: DashboardView // Tableau de bord principal (GET /api/admin/dashboard_stats)
        },
        {
          path: 'students',
          name: 'StudentsAdmin',
          component: StudentsAdminView // Gestion Étudiants (Liste/Cartes/CRUD)
        },
        {
          path: 'payments',
          name: 'PaymentsAdmin',
          component: PaymentsAdminView // Gestion Paiements (CRUD)
        },
        {
          path: 'reports',
          name: 'ReportsAdmin',
          component: ReportsAdminView // Génération Rapports (CSV/PDF)
        },

        {
          path: '/admin/academic-config',
          name: 'AcademicConfig', //Gesstin de la srtucturation
          component: AcademicConfigView
        },
        {
          path: '/scan-config',
          name: 'ScanConfig',
          component: ScanConfigView, // Configuration du Point d'Accès
          meta: { requiresAuth: false } // Rendu public, mais l'usage est réservé à l'Admin
        },
      ]
    },

    // =======================================================
    // 4. ROUTE D'ERREUR
    // =======================================================
    {
      path: '/:catchAll(.*)',
      name: 'NotFound',
      component: NotFoundView
    }
  ]
})

// =======================================================
// Global Navigation Guard (Protection des routes ADMIN)
// =======================================================
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Si la route exige l'authentification et que l'utilisateur n'est pas connecté
    next({ name: 'Login', query: { redirect: to.fullPath } }) // Rediriger vers la connexion
  } else if ((to.name === 'Login') && authStore.isAuthenticated) {
    // Si l'utilisateur est déjà connecté et tente d'accéder à la page de connexion ou d'accueil
    next({ name: 'AdminDashboard' }) // Rediriger vers le tableau de bord
  } else {
    // Continuer la navigation
    next()
  }
})

export default router