<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const tripName = ref('')
const memberName = ref('')
const members = ref([])
const isLoading = ref(false)
const trips = ref([])
const API_URL = 'http://localhost:8002'

const fetchTrips = async () => {
  try {
    const res = await fetch(`${API_URL}/trips`)
    if (res.ok) {
      trips.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to fetch trips', e)
  }
}

onMounted(fetchTrips)

const addMember = () => {
  if (memberName.value.trim()) {
    members.value.push(memberName.value.trim())
    memberName.value = ''
  }
}

const removeMember = (index) => {
  members.value.splice(index, 1)
}

const createTrip = async () => {
  if (!tripName.value || members.value.length === 0) return
  
  isLoading.value = true
  try {
    // 1. Create Trip
    const tripRes = await fetch(`${API_URL}/trips?name=` + encodeURIComponent(tripName.value), {
      method: 'POST'
    })
    const trip = await tripRes.json()
    
    // 2. Add Members
    for (const member of members.value) {
      await fetch(`${API_URL}/trips/${trip.id}/members`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: member })
      })
    }
    
    // Navigate to Dashboard
    router.push({ name: 'dashboard', params: { tripId: trip.id } })
    
  } catch (e) {
    console.error(e)
    alert('建立旅程失敗')
  } finally {
    isLoading.value = false
  }
}

const toggleStatus = async (trip) => {
  const newStatus = trip.status === 'active' ? 'settled' : 'active'
  try {
    const res = await fetch(`${API_URL}/trips/${trip.id}?status=${newStatus}`, {
      method: 'PATCH'
    })
    if (res.ok) {
      trip.status = newStatus
    }
  } catch (e) {
    console.error('Failed to update status', e)
  }
}

const deleteTrip = async (trip) => {
  if (!confirm(`確定要刪除旅程 "${trip.name}" 嗎？此動作無法復原。`)) return

  try {
    const res = await fetch(`${API_URL}/trips/${trip.id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      // Remove from local list
      trips.value = trips.value.filter(t => t.id !== trip.id)
    }
  } catch (e) {
    console.error('Failed to delete trip', e)
    alert('刪除失敗')
  }
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-extrabold text-gray-900 sm:text-4xl">
        <span class="block">旅程管理</span>
        <span class="block text-indigo-600 text-lg font-medium mt-2">輕鬆建立與管理您的每一次出遊</span>
      </h1>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Create New Trip Section -->
      <div class="lg:col-span-5">
        <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 sticky top-6">
          <div class="bg-indigo-600 px-6 py-4">
            <h2 class="text-xl font-bold text-white flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              建立新旅程
            </h2>
          </div>
          
          <div class="p-6 space-y-6">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">旅程名稱</label>
              <div class="relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 sm:text-sm">✈️</span>
                </div>
                <input 
                  v-model="tripName" 
                  class="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md py-3 border" 
                  type="text" 
                  placeholder="例如：東京五日遊"
                >
              </div>
            </div>
            
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">新增成員</label>
              <div class="flex gap-2">
                <input 
                  v-model="memberName" 
                  @keyup.enter="addMember" 
                  class="focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md py-2 px-3 border" 
                  type="text" 
                  placeholder="輸入名字按 Enter"
                >
                <button 
                  @click="addMember" 
                  class="bg-indigo-100 text-indigo-700 hover:bg-indigo-200 font-bold py-2 px-4 rounded-md transition duration-150 ease-in-out"
                >
                  新增
                </button>
              </div>
            </div>
            
            <div>
              <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">成員名單</h3>
              <div class="flex flex-wrap gap-2 min-h-[3rem] p-3 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                <TransitionGroup name="list">
                  <span 
                    v-for="(m, index) in members" 
                    :key="m" 
                    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800"
                  >
                    {{ m }}
                    <button 
                      @click="removeMember(index)" 
                      class="ml-2 inline-flex items-center justify-center h-4 w-4 rounded-full text-indigo-400 hover:bg-indigo-200 hover:text-indigo-600 focus:outline-none"
                    >
                      <svg class="h-3 w-3" stroke="currentColor" fill="none" viewBox="0 0 8 8">
                        <path stroke-linecap="round" stroke-width="1.5" d="M1 1l6 6m0-6L1 7" />
                      </svg>
                    </button>
                  </span>
                </TransitionGroup>
                <span v-if="members.length === 0" class="text-gray-400 text-sm self-center">尚未新增成員</span>
              </div>
            </div>
            
            <button 
              @click="createTrip" 
              :disabled="isLoading || !tripName || members.length === 0" 
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150 ease-in-out"
            >
              <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isLoading ? '建立中...' : '開始旅程' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Existing Trips List -->
      <div class="lg:col-span-7">
        <div class="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100 h-full">
          <div class="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 class="text-xl font-bold text-gray-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              現有旅程
            </h2>
            <span class="bg-gray-200 text-gray-700 py-1 px-3 rounded-full text-xs font-bold">{{ trips.length }} 個旅程</span>
          </div>
          
          <div class="p-6 bg-gray-50/50 h-full min-h-[400px]">
            <div v-if="trips.length > 0" class="grid gap-4">
              <TransitionGroup name="list">
                <div 
                  v-for="trip in trips" 
                  :key="trip.id" 
                  class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition duration-200 group"
                >
                  <div class="flex justify-between items-start">
                    <div>
                      <h3 
                        class="text-lg font-bold text-gray-900 group-hover:text-indigo-600 transition cursor-pointer"
                        @click="router.push({ name: 'dashboard', params: { tripId: trip.id } })"
                      >
                        {{ trip.name }}
                      </h3>
                      <p class="text-sm text-gray-500 mt-1 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                        {{ trip.members.length }} 位成員: {{ trip.members.join(', ') }}
                      </p>
                    </div>
                    <button 
                      @click.stop="toggleStatus(trip)"
                      class="px-3 py-1 rounded-full text-xs font-bold border transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2"
                      :class="trip.status === 'active' 
                        ? 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100 focus:ring-green-500' 
                        : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200 focus:ring-gray-500'"
                    >
                      <span class="flex items-center">
                        <span class="h-2 w-2 rounded-full mr-1.5" :class="trip.status === 'active' ? 'bg-green-500' : 'bg-gray-400'"></span>
                        {{ trip.status === 'active' ? '進行中' : '已結算' }}
                      </span>
                    </button>
                  </div>
                  
                  <div class="mt-4 pt-4 border-t border-gray-50 flex justify-between items-center">
                    <button 
                      @click.stop="deleteTrip(trip)"
                      class="text-red-400 hover:text-red-600 text-sm font-medium flex items-center transition px-2 py-1 rounded hover:bg-red-50"
                      title="刪除旅程"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      刪除
                    </button>
                    
                    <button 
                      @click="router.push({ name: 'dashboard', params: { tripId: trip.id } })" 
                      class="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center transition"
                    >
                      進入旅程 
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                      </svg>
                    </button>
                  </div>
                </div>
              </TransitionGroup>
            </div>
            <div v-else class="flex flex-col items-center justify-center h-full text-gray-400 py-12">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <p>目前沒有旅程記錄</p>
              <p class="text-sm mt-2">在左側建立您的第一個旅程吧！</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.list-move, /* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
  position: absolute;
}
</style>
