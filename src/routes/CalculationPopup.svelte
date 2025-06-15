<script>
    export let calculationOpen;
</script>

<div class="absolute border border-gray-400 top-10 right-1/2 translate-x-1/2 z-50 bg-gray-100 rounded-xl shadow-xl p-6 max-w-md text-gray-800">
  <div class="flex flex-col items-center gap-4 mb-6">
    <span class="text-lg font-semibold">Calculation Used:</span>
    <img src="/equation.svg" alt="Calculation equation" class="w-full max-w-xs" />
  </div>

  <div class="space-y-2">
    <span class="text-lg font-semibold">Current Version Details:</span>
    <ul class=" list-disc list-inside text-sm text-gray-700">
      <li class="textl">Previous year sales are considered from <strong>2024-03-01</strong> to <strong>2025-03-01</strong>.</li>
      <li class="textl">Forecasted sales are based on your selected filter time frame.</li>
    </ul>
  </div>

  <button on:click={() => calculationOpen = false} class="absolute top-2 right-5 text-lg text-red-400">x</button>
</div>
