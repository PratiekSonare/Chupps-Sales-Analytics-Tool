<script>
      let expand_rotate = false;
</script>

<button
    class="z-100 p-0 mt-2 cursor-pointer transition-transform duration-300 ease-in-out {expand_rotate
    ? 'rotate-[360deg]'
    : ''}"
    on:click={() => (expand_rotate = !expand_rotate)}
>
    <img
    src="/chupps-white.svg"
    alt=""
    class="invert block h-auto mt-3"
    style="width: 25px;"
    />
</button>