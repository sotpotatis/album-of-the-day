<!-- Popup.svelte
A closable popup window. -->
<script>
	import { createEventDispatcher } from 'svelte';
	import Icon from './Icon.svelte';
	import Button from './Button.svelte';
	export let title;
	export let description;
	const dispatch = createEventDispatcher();
	const onClose = () => {
		// Dispatch an event to tell that the popup was closed. Learned this along the way of developing this app.
		// I really like this Svelte feature. Sorry if it isn't implemented everywhere!
		dispatch('popupclose');
	};
</script>

<div
	class="fixed top-0 left-0 min-h-screen min-w-full p-8 z-10 text-albumOfTheDay-text-foreground backdrop-blur-md"
	on:popupclose
>
	<div class="flex flex-col items-center justify-center min-w-full min-h-screen">
		<!-- Add a close button -->
		<Button text="Stäng" backgroundColor="gray-800" textColor="white" on:click={onClose}>
			<svelte:fragment slot="icon">
				<Icon name="iconamoon:close-fill" color="white" />
			</svelte:fragment>
		</Button>
		<div
			class="z-20 w-full h-full md:w-1/2 lg:w-1/3 bg-albumOfTheDay-uiElements-darkBackground border-2 rounded-lg p-12 mt-3 flex flex-col gap-x-8 gap-y-4 md:gap-y-8 items-center justify-center"
		>
			<h1 class="text-3xl font-bold py-3">{title}</h1>
			<p class="py-3">{description}</p>
			<slot name="content" />
		</div>
	</div>
</div>
