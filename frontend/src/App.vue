<script setup>
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900 font-sans">
    <header class="bg-indigo-600 text-white p-4 shadow-md">
      <div class="container mx-auto flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold hover:text-indigo-100">BestFriend</router-link>
        <nav class="space-x-4">
          <!-- Navigation links can go here -->
        </nav>
      </div>
    </header>
    <main class="container mx-auto p-4">
      <router-view></router-view>
    </main>
  </div>
</template>
