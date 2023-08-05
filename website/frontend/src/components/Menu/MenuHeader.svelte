<!-- MenuHeader.svelte
Menu header to display when the menu is open.
Includes menu button and a "change font" button -->
<script>
	import MenuIcon from './MenuIcon.svelte';
	import FontToggle from './FontToggle.svelte';
	export let toggleCollapsed; // Function to toggle if the menu is collapsed or not
</script>

<div class="min-w-screen flex flex-row pb-12 justify-between">
	<MenuIcon collapsed={false} animate={true} {toggleCollapsed} />
	<FontToggle on:fontchange />
</div>
