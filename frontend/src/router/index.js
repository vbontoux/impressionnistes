import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

// Lazy load views
const Home = () => import('../views/Home.vue');
const Login = () => import('../views/Login.vue');
const Register = () => import('../views/Register.vue');
const VerifyEmail = () => import('../views/VerifyEmail.vue');
const Callback = () => import('../views/Callback.vue');
const Dashboard = () => import('../views/Dashboard.vue');
const CrewMembers = () => import('../views/CrewMembers.vue');
const Boats = () => import('../views/Boats.vue');
const BoatDetail = () => import('../views/BoatDetail.vue');
const Payment = () => import('../views/Payment.vue');
const PaymentCheckout = () => import('../views/PaymentCheckout.vue');
const PaymentSuccess = () => import('../views/PaymentSuccess.vue');
const Profile = () => import('../views/Profile.vue');
const AdminDashboard = () => import('../views/admin/AdminDashboard.vue');
const AdminEventConfig = () => import('../views/admin/AdminEventConfig.vue');
const AdminPricingConfig = () => import('../views/admin/AdminPricingConfig.vue');
const AdminCrewMembers = () => import('../views/admin/AdminCrewMembers.vue');
const AdminBoats = () => import('../views/admin/AdminBoats.vue');
const AdminDataExport = () => import('../views/admin/AdminDataExport.vue');
const AdminClubManagers = () => import('../views/admin/AdminClubManagers.vue');
const PrivacyPolicy = () => import('../views/legal/PrivacyPolicy.vue');
const TermsConditions = () => import('../views/legal/TermsConditions.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true },
  },
  {
    path: '/verify-email',
    name: 'VerifyEmail',
    component: VerifyEmail,
    meta: { guest: true },
  },
  {
    path: '/callback',
    name: 'Callback',
    component: Callback,
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy,
  },
  {
    path: '/terms-conditions',
    name: 'TermsConditions',
    component: TermsConditions,
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/crew',
    name: 'CrewMembers',
    component: CrewMembers,
    meta: { requiresAuth: true },
  },
  {
    path: '/boats',
    name: 'Boats',
    component: Boats,
    meta: { requiresAuth: true },
  },
  {
    path: '/boats/:id',
    name: 'BoatDetail',
    component: BoatDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/payment',
    name: 'Payment',
    component: Payment,
    meta: { requiresAuth: true },
  },
  {
    path: '/payment/checkout',
    name: 'PaymentCheckout',
    component: PaymentCheckout,
    meta: { requiresAuth: true },
  },
  {
    path: '/payment/success',
    name: 'PaymentSuccess',
    component: PaymentSuccess,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/events',
    name: 'AdminEventConfig',
    component: AdminEventConfig,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/pricing',
    name: 'AdminPricingConfig',
    component: AdminPricingConfig,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/crew',
    name: 'AdminCrewMembers',
    component: AdminCrewMembers,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/boat-registrations',
    name: 'AdminBoats',
    component: AdminBoats,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/exports',
    name: 'AdminDataExport',
    component: AdminDataExport,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/admin/club-managers',
    name: 'AdminClubManagers',
    component: AdminClubManagers,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  }
  // Check if route requires admin access
  else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    console.warn('Access denied: Admin privileges required');
    next('/dashboard');
  }
  // Check if route is for guests only (login/register)
  else if (to.meta.guest && isAuthenticated) {
    next('/dashboard');
  }
  else {
    next();
  }
});

export default router;
