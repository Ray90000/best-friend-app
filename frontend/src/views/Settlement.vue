<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const tripId = route.params.tripId

const transfers = ref([])
const isLoading = ref(true)
const API_URL = 'http://localhost:8002'

onMounted(async () => {
  try {
    const res = await fetch(`${API_URL}/trips/${tripId}/settlement`)
    if (!res.ok) throw new Error('Failed to load settlement')
    const data = await res.json()
    transfers.value = data.transfers
  } catch (e) {
    console.error(e)
    alert('Error loading settlement')
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-indigo-800">結算清單</h2>
      <button @click="router.push({ name: 'dashboard', params: { tripId } })" class="text-gray-500 hover:text-gray-700">返回儀表板</button>
    </div>
    
    <div v-if="isLoading" class="text-center p-10">
      計算中...
    </div>
    
    <div v-else-if="transfers.length > 0" class="bg-white rounded-xl shadow-md overflow-hidden">
      <div class="p-6">
        <p class="mb-4 text-gray-600">以下是最佳轉帳建議，可結清所有債務：</p>
        <ul class="space-y-4">
          <li v-for="(t, i) in transfers" :key="i" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-red-500">{{ t.from_member }}</span>
              <span class="text-gray-400">➜</span>
              <span class="font-bold text-green-500">{{ t.to_member }}</span>
            </div>
            <span class="text-xl font-bold text-indigo-600">${{ t.amount.toFixed(2) }}</span>
          </li>
        </ul>
      </div>
    </div>
    
    <div v-else class="bg-white rounded-xl shadow-md p-10 text-center">
      <p class="text-xl text-gray-600 font-medium">全部結清！ 🎉</p>
      <p class="text-gray-400 mt-2">目前沒有人欠錢。</p>
    </div>
  </div>
</template>
