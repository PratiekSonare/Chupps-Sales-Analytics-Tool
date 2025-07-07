<!-- src/components/Loading.svelte -->
<script>
  export let visible = false;
</script>

{#if visible}
  <div class="loader-backdrop">
    <div class="loader-container">
      <svg width="50" height="50" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="40" stroke="#000" stroke-width="10" stroke-linecap="round">
          <animate attributeName="stroke-opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  </div>
{/if}

<style>
  .loader-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(255, 255, 255, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
  }

  .loader-container svg {
    animation: blink 1s infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
</style>
