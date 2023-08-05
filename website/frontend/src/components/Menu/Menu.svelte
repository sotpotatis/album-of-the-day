<!-- Menu.svelte
The main menu on the website.
-->
<script>
	import MenuIcon from './MenuIcon.svelte';
	import MenuItem from './MenuItem.svelte';
	import MenuHeader from './MenuHeader.svelte';
	const menuItems = [
		{
			name: 'hem',
			url: '/'
		},
		{
			name: 'album',
			url: '/album-of-the-days'
		},
		{
			name: 'genrer',
			url: '/genres'
		},
		{
			name: 'listor',
			url: '/lists'
		},
		{
			name: 'rotationer',
			url: '/daily-rotations'
		}
	];
	export let toggleCollapsed; // Function to toggle if the menu is collapsed or not
</script>

<nav id="menu" class="flex flex-col min-h-screen min-w-screen p-12 text-left">
	<MenuHeader {toggleCollapsed} on:fontchange />
	<ul
		id="menu-items"
		class="animate-grow list-none min-h-full flex flex-col shrink grow items-evenly text-center justify-evenly"
	>
		<!-- Render all menu items -->
		{#each menuItems as menuItem}
			<MenuItem text={menuItem.name} url={menuItem.url} />
		{/each}
	</ul>
</nav>
