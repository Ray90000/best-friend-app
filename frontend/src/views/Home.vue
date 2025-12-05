<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const features = [
  {
    title: 'FairShare 分帳計算機',
    description: '輕鬆與朋友分攤旅費，智慧結算最少轉帳次數。',
    icon: '✈️',
    route: 'setup',
    color: 'bg-indigo-500'
  },
  // Future features can be added here
  {
    title: '敬請期待',
    description: '更多精彩功能即將推出！',
    icon: '🚀',
    route: '',
    color: 'bg-gray-400'
  }
]

const navigateTo = (routeName) => {
  if (routeName) {
    router.push({ name: routeName })
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-10">
    <div class="text-center mb-12">
      <h1 class="text-4xl font-extrabold text-gray-900 mb-4">歡迎使用好朋友 App</h1>
      <p class="text-xl text-gray-600">您的團體活動與旅遊最佳夥伴。</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div 
        v-for="feature in features" 
        :key="feature.title"
        @click="navigateTo(feature.route)"
        class="bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer transform transition duration-300 hover:scale-105 hover:shadow-xl"
        :class="{ 'opacity-75 cursor-not-allowed': !feature.route }"
      >
        <div :class="`${feature.color} h-2`"></div>
        <div class="p-6">
          <div class="text-4xl mb-4">{{ feature.icon }}</div>
          <h3 class="text-2xl font-bold text-gray-800 mb-2">{{ feature.title }}</h3>
          <p class="text-gray-600">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
