<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const tripId = route.params.tripId;

const trip = ref(null);
const payer = ref("");
const amount = ref("");
const what = ref("");
const forWhom = ref([]); // Selected members
const isLoading = ref(false);

const API_URL = "";

onMounted(async () => {
  try {
    const res = await fetch(`${API_URL}/trips/${tripId}`);
    if (!res.ok) throw new Error("Trip not found");
    trip.value = await res.json();
    // Default forWhom to all members
    forWhom.value = [...trip.value.members];
  } catch (e) {
    console.error(e);
    alert("Error loading trip");
    router.push("/");
  }
});

const submitTransaction = async () => {
  if (
    !payer.value ||
    !amount.value ||
    !what.value ||
    forWhom.value.length === 0
  )
    return;

  isLoading.value = true;
  try {
    const res = await fetch(`${API_URL}/trips/${tripId}/transactions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        payer: payer.value,
        amount: parseFloat(amount.value),
        what: what.value,
        for_whom: forWhom.value,
      }),
    });

    if (!res.ok) throw new Error("Failed to add transaction");

    // Go back to dashboard
    router.push({ name: "dashboard", params: { tripId } });
  } catch (e) {
    console.error(e);
    alert("新增消費失敗");
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div
    v-if="trip"
    class="max-w-md mx-auto bg-white rounded-xl shadow-md overflow-hidden md:max-w-2xl p-6"
  >
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-indigo-700">新增消費</h2>
      <button
        @click="router.push({ name: 'dashboard', params: { tripId } })"
        class="text-gray-500 hover:text-gray-700"
      >
        取消
      </button>
    </div>

    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2"
        >誰先墊錢？</label
      >
      <select
        v-model="payer"
        class="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      >
        <option disabled value="">選擇付款人</option>
        <option v-for="m in trip.members" :key="m" :value="m">{{ m }}</option>
      </select>
    </div>

    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2">金額 ($)</label>
      <input
        v-model="amount"
        type="number"
        step="0.01"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        placeholder="0.00"
      />
    </div>

    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2">項目名稱</label>
      <input
        v-model="what"
        type="text"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        placeholder="例如：晚餐"
      />
    </div>

    <div class="mb-6">
      <label class="block text-gray-700 text-sm font-bold mb-2"
        >分攤對象 (誰有份？)</label
      >
      <div class="grid grid-cols-2 gap-2">
        <div v-for="m in trip.members" :key="m" class="flex items-center">
          <input
            type="checkbox"
            :id="m"
            :value="m"
            v-model="forWhom"
            class="mr-2"
          />
          <label :for="m">{{ m }}</label>
        </div>
      </div>
    </div>

    <button
      @click="submitTransaction"
      :disabled="
        isLoading || !payer || !amount || !what || forWhom.length === 0
      "
      class="w-full bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50 disabled:cursor-not-allowed transition duration-150 ease-in-out"
    >
      {{ isLoading ? "儲存中..." : "儲存消費" }}
    </button>
  </div>
  <div v-else class="text-center p-10">載入中...</div>
</template>
