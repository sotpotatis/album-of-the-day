<!-- Page.svelte
A layout page component that includes a header and a body. This component should
be used by all pages on the website to ensure a consistent styling.
-->
<script>
	import Header from './Header/Header.svelte';
	import Cookies from 'js-cookie';
	import { getFontFamily } from '../lib/font.js';
	import SearchUI from './SearchUI/SearchUI.svelte';
	export let fullScreenHeader = false; // Can be set so the header covers the whole screen
	// Determine what font family to use: the user can enable dyslexic font if wanted.
	const fontFamiliesToClasses = {
		default: 'font-default',
		dyslexic: 'font-dyslexic'
	};
	let fontFamily = getFontFamily();
	console.log(`Using font family: ${fontFamily}.`);
	// Variables related to the page menu
	let menuCollapsed = true;
	// ...and to the search
	let searchShown = false;
	let toggleMenuCollapsed = () => {
		menuCollapsed = !menuCollapsed;
	};
	let toggleSearch = () => {
		console.log(`Toggling search.`);
		searchShown = !searchShown;
	};
</script>

{#if searchShown}
	<SearchUI {toggleSearch} />
{/if}
<div
	class={`min-w-full text-center ${fontFamiliesToClasses[fontFamily]} ${
		searchShown ? `blur-lg` : ''
	}`}
>
	<!-- Create a header -->
	<Header
		fullScreen={fullScreenHeader}
		{menuCollapsed}
		{toggleMenuCollapsed}
		{toggleSearch}
		on:fontchange={() => {
			fontFamily = getFontFamily();
		}}
	>
		{#if menuCollapsed}
			<slot name="header" />
		{/if}
	</Header>
	<!-- ...and a body...
    (that should only be shown if the menu is collapsed) -->
	{#if menuCollapsed}
		<main class="p-3 flex flex-col justify-center text-albumOfTheDay-text-foreground gap-y-2">
			<slot name="page" />
		</main>
	{/if}
</div>
