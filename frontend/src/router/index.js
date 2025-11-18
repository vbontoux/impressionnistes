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
  // Check if route is for guests only (login/register)
  else if (to.meta.guest && isAuthenticated) {
    next('/dashboard');
  }
  else {
    next();
  }
});

export default router;
