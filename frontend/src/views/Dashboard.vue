<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const tripId = route.params.tripId

const trip = ref(null)
const API_URL = '/trips'

onMounted(async () => {
  try {
    const res = await fetch(`${API_URL}/trips/${tripId}`)
    if (!res.ok) throw new Error('Trip not found')
    trip.value = await res.json()
  } catch (e) {
    console.error(e)
    alert('Error loading trip')
    router.push('/')
  }
})

const totalSpend = computed(() => {
  if (!trip.value) return 0
  return trip.value.transactions.reduce((sum, t) => sum + t.amount, 0)
})

const memberSpends = computed(() => {
  if (!trip.value) return {}
  const spends = {}
  trip.value.members.forEach(m => spends[m] = 0)
  
  trip.value.transactions.forEach(t => {
    // This is "Personal Spend" (consumption), not "Amount Paid" (fronted)
    // Logic: If t.for_whom has N people, each spent amount/N
    if (t.for_whom && t.for_whom.length > 0) {
      const split = t.amount / t.for_whom.length
      t.for_whom.forEach(m => {
        if (spends[m] !== undefined) spends[m] += split
      })
    }
  })
  return spends
})

const memberPaid = computed(() => {
    if (!trip.value) return {}
    const paid = {}
    trip.value.members.forEach(m => paid[m] = 0)
    trip.value.transactions.forEach(t => {
        if (paid[t.payer] !== undefined) paid[t.payer] += t.amount
    })
    return paid
})

const mvp = computed(() => {
  if (!trip.value) return null
  const paid = memberPaid.value
  let max = -1
  let mvpName = ''
  for (const [name, amount] of Object.entries(paid)) {
    if (amount > max) {
      max = amount
      mvpName = name
    }
  }
  return { name: mvpName, amount: max }
})

const deleteTransaction = async (transaction) => {
  if (!confirm(`確定要刪除 "${transaction.what}" 這筆消費嗎？`)) return

  try {
    const res = await fetch(`${API_URL}/trips/${tripId}/transactions/${transaction.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      // Reload trip data to update stats
      const updatedTrip = await res.json()
      trip.value = updatedTrip
    }
  } catch (e) {
    console.error('Failed to delete transaction', e)
    alert('刪除失敗')
  }
}
</script>

<template>
  <div v-if="trip" class="max-w-4xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <div>
        <div class="flex items-center text-sm text-gray-500 mb-1">
          <router-link to="/" class="hover:text-indigo-600">首頁</router-link>
          <span class="mx-2">/</span>
          <router-link to="/setup" class="hover:text-indigo-600">旅程管理</router-link>
        </div>
        <h2 class="text-3xl font-bold text-indigo-800">{{ trip.name }}</h2>
      </div>
      <div class="space-x-2">
        <button @click="router.push({ name: 'transaction', params: { tripId } })" class="bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">
          + 新增消費
        </button>
        <button @click="router.push({ name: 'settlement', params: { tripId } })" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
          $ 結算
        </button>
      </div>
    </div>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
        <h3 class="text-gray-500 text-sm uppercase font-bold">總支出</h3>
        <p class="text-3xl font-bold text-gray-800">${{ totalSpend.toFixed(2) }}</p>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
        <h3 class="text-gray-500 text-sm uppercase font-bold">MVP (墊付最多)</h3>
        <p class="text-2xl font-bold text-gray-800">{{ mvp.name }}</p>
        <p class="text-sm text-gray-600">${{ mvp.amount.toFixed(2) }}</p>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
        <h3 class="text-gray-500 text-sm uppercase font-bold">成員人數</h3>
        <p class="text-3xl font-bold text-gray-800">{{ trip.members.length }}</p>
      </div>
    </div>
    
    <!-- Personal Spends -->
    <div class="bg-white rounded-lg shadow-md overflow-hidden mb-8">
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 class="font-bold text-gray-700">個人消費 (實際應付)</h3>
      </div>
      <div class="p-6">
        <div v-for="(amount, name) in memberSpends" :key="name" class="flex justify-between items-center border-b border-gray-100 py-2 last:border-0">
          <span class="font-medium text-gray-700">{{ name }}</span>
          <span class="font-bold text-gray-900">${{ amount.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 class="font-bold text-gray-700">最近消費記錄</h3>
      </div>
      <div class="p-6">
        <ul v-if="trip.transactions.length > 0">
            <li v-for="(t, i) in trip.transactions.slice().reverse()" :key="t.id || i" class="mb-3 pb-3 border-b border-gray-100 last:border-0 last:pb-0 last:mb-0 group">
                <div class="flex justify-between items-start">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-bold text-gray-800">{{ t.what }}</span>
                            <span class="font-bold text-indigo-600">${{ t.amount.toFixed(2) }}</span>
                        </div>
                        <div class="text-sm text-gray-500">
                            由 <span class="font-medium text-gray-700">{{ t.payer }}</span> 支付
                            <span class="italic">({{ t.for_whom.join(', ') }})</span>
                        </div>
                    </div>
                    <button 
                        @click="deleteTransaction(t)"
                        class="text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1"
                        title="刪除消費"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </li>
        </ul>
        <p v-else class="text-gray-400 italic text-center">尚無消費記錄。</p>
      </div>
    </div>
    
  </div>
  <div v-else class="text-center p-10">
    載入中...
  </div>
</template>
