<!-- Header.svelte
Creates a header which is the top of the webpage that has a distinct color and header items.
For different header components based on subpages, see the other files in this directory
-->
<script>
	import Menu from '../Menu/Menu.svelte';
	import MenuIcon from '../Menu/MenuIcon.svelte';
	import SearchBarButton from '../SearchUI/SearchBarButton.svelte';
	// Variables related to the page menu
	export let menuCollapsed;
	export let toggleMenuCollapsed;
	// Related to the search bar, should be passed
	export let toggleSearch;
	export let fullScreen; // Whether to cover the full screen or not.
</script>

<!-- Set full-screen menu if the menu is open -->
{#if !menuCollapsed}
	<Menu toggleCollapsed={toggleMenuCollapsed} on:fontchange />
{:else}
	<header class={`bg-blue-800 p-12 text-white${fullScreen ? ' h-screen' : ''}`}>
		<div class={`min-w-screen flex justify-between text-left pb-6 md:pb-0`}>
			<MenuIcon collapsed={menuCollapsed} toggleCollapsed={toggleMenuCollapsed} />
			<SearchBarButton {toggleSearch} />
		</div>
		<slot />
	</header>
{/if}
