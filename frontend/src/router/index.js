import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Dashboard from '@/views/Dashboard.vue'
import ChatView from '@/views/ChatView.vue'
import DocumentLibrary from '@/views/DocumentLibrary.vue'
import PPTPreviewView from '@/views/PPTPreviewView.vue'
import TemplateManagement from '@/views/TemplateManagement.vue'
import DigitalHuman from '@/views/DigitalHuman.vue'
import Community from '@/views/Community.vue'
import UserProfileOnboarding from '@/views/UserProfileOnboarding.vue'
import UserProfileCenter from '@/views/UserProfileCenter.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/chat/:id?',
    name: 'Chat',
    component: ChatView,
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    name: 'Documents',
    component: DocumentLibrary,
    meta: { requiresAuth: true }
  },
  {
    path: '/ppt/:id',
    name: 'PPTWopi',
    component: PPTPreviewView,
    meta: { requiresAuth: true }
  },
  {
    path: '/templates',
    name: 'TemplateManagement',
    component: TemplateManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/avatar',
    name: 'DigitalHuman',
    component: DigitalHuman,
    meta: { requiresAuth: true }
  },
  {
    path: '/community',
    name: 'Community',
    component: Community,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile-onboarding',
    name: 'UserProfileOnboarding',
    component: UserProfileOnboarding,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfileCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile-center',
    name: 'UserProfileCenter',
    component: UserProfileCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/share/:token',
    name: 'SharedConversation',
    component: () => import('@/views/SharedConversationView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/share-cop/:token',
    name: 'CollabConversation',
    component: () => import('@/views/CollabConversationView.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Allow collab access without auth
    if (to.name === 'Chat' && to.query.collab === 'true') {
      next()
    } else {
      next('/login')
    }
  } else {
    next()
  }
})

export default router
