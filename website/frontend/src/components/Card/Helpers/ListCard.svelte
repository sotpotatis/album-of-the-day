<!-- ListCard.svelte
A helper card that automagically fills out information for an album list
based on its data. -->
<script>
	import Card from '../Card.svelte';
	import Image from '../../Generic/Image.svelte';
	import CardBody from '../CardBody.svelte';
	import { dateDifferenceToHumanReadable } from '../../../lib/dates.js';
	export let data; // List data
	export let skeleton = false;
	export let featured = false; // Can be used to set a card as featured
</script>

<Card {skeleton} color={featured ? 'dark' : 'light'}>
	<svelte:fragment slot="title">
		{#if featured}
			<h2 class="text-albumOfTheDay-text-foreground text-2xl">
				<span class="font-bold">I blickfånget</span>
			</h2>
		{/if}
	</svelte:fragment>
	<svelte:fragment slot="image" />
	<svelte:fragment slot="body">
		<CardBody text={data.description} title={data.name} summary={data.description} {skeleton} />
		<!-- Add date when the list was created -->
		<p class={skeleton ? 'bg-albumOfTheDay-text-foreground p-3' : ''}>
			{!skeleton ? dateDifferenceToHumanReadable(data.created_at, true) : 'x månad år'}
		</p>
		<a
			href={!skeleton ? `/lists/${data.id}` : null}
			class={skeleton ? 'bg-albumOfTheDay-text-foreground' : ''}>Till lista >></a
		>
	</svelte:fragment>
</Card>
