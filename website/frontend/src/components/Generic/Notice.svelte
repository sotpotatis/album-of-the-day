<!-- Notice.svelte
A notice that can be added for extra attention.
Like a callout. Design is similar to Card (see the ../Card directory),
but it has another purpose.
-->
<script>
	export let title;
	export let description;
	export let backgroundColor = 'red-100';
	export let borderColor = 'red-200';
	export let textColor = 'albumOfTheDay-text-foreground';
	export let includeIcon = false; // Set to true to allow for an icon-like layout
	export let closable = true; // Set to false to not allow the dialog to close
	export let skeleton = false; // Set to true to render skeleton loader
	let closed = false;
</script>

{#if !closed}
	<div
		class={`bg-${backgroundColor} text-${textColor} p-3 border-2 border-${borderColor} rounded-lg p-6${
			includeIcon ? ' flex flex-col md:flex-row justify-center items-center' : ''
		}${skeleton ? ' animate-pulse' : ''}`}
	>
		<!-- Provide a slot for adding content. Note that includeIcon must also be set to
        true for it to render properly -->
		<slot name="icon" />
		<div>
			<h2 class={`font-bold md:text-lg  py-3${skeleton ? ` bg-${textColor} m-6` : ''}`}>{title}</h2>
			<p class={`text-sm md:text-base ${skeleton ? ` bg-${textColor} m-6` : ''}`}>{description}</p>
			<!-- Add close button if enabled -->
			{#if closable}
				<button
					class={`underline${skeleton ? ` bg-${textColor} m-6` : ''}`}
					on:click={!skeleton
						? () => {
								closed = true;
						  }
						: null}>Stäng</button
				>
			{/if}
			<!-- Provide a slot for other content -->
			<slot name="content" />
		</div>
	</div>
{/if}
