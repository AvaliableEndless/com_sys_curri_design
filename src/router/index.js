import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/',
    redirect: '/owners',
    meta: { requiresAuth: true }
  },
  {
    path: '/owners',
    name: 'Owners',
    component: () => import('../views/OwnerList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/houses',
    name: 'Houses',
    component: () => import('../views/HouseList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/payment-bills',
    name: 'PaymentBills',
    component: () => import('../views/PaymentBillList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/violation-bills',
    name: 'ViolationBills',
    component: () => import('../views/ViolationBillList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/complaint-bills',
    name: 'ComplaintBills',
    component: () => import('../views/ComplaintBillList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/repair-bills',
    name: 'RepairBills',
    component: () => import('../views/RepairBillList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/repair-workers',
    name: 'RepairWorkers',
    component: () => import('../views/RepairWorkerList.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated')
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 