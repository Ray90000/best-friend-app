import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import TripSetup from '../views/TripSetup.vue'
import TransactionEntry from '../views/TransactionEntry.vue'
import Dashboard from '../views/Dashboard.vue'
import Settlement from '../views/Settlement.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/setup',
            name: 'setup',
            component: TripSetup
        },
        {
            path: '/transaction/:tripId',
            name: 'transaction',
            component: TransactionEntry
        },
        {
            path: '/dashboard/:tripId',
            name: 'dashboard',
            component: Dashboard
        },
        {
            path: '/settlement/:tripId',
            name: 'settlement',
            component: Settlement
        }
    ]
})

export default router
