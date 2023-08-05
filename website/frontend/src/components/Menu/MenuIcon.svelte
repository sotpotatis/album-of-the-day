<!-- MenuIcon.svelte
The menu icon used for toggling the menu. -->
<script>
	import Icon from '../Generic/Icon.svelte';
	export let collapsed; // Whether the menu is open or not
	export let toggleCollapsed; // Function to toggle the menu
	export let animate = false; // Whether to play a "clicked" animation
</script>

<button on:click={toggleCollapsed} class={animate ? 'animate-spinAround' : ''}>
	<Icon size="small" name="fa6-solid:bars" color={collapsed ? 'white' : 'gray-400'} />
</button>
