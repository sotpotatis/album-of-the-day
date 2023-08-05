<!-- Individual list page
A page for an individual list item. -->
<script>
	import { onMount } from 'svelte';
	import { DUMMY_LIST_DATA } from '../../../lib/dummyData.js';
	import { getList } from '../../../lib/apiClient.js';
	import Page from '../../../components/Page.svelte';
	import HeadingDivider from '../../../components/Generic/HeadingDivider.svelte';
	import AlbumCard from '../../../components/Card/Helpers/AlbumCard.svelte';
	import ListHeader from '../../../components/Header/ListHeader.svelte';
	import { DateTime } from 'luxon';
	import Error from '../../../components/Generic/Error.svelte';
	import { MANUAL_URLS_NOTICE } from '../../../lib/utilities.js';
	export let data; // This will contain the requested ID.
	$: requestedId = data.id;
	let [success, responseData] = [null, DUMMY_LIST_DATA]; // Set success to null to indicate a skeleton loader and load dummy data
	onMount(() => {
		getList(requestedId).then((result) => {
			[success, responseData] = result;
		});
	});
	$: skeleton = success !== true; // Whether to show a skeleton loader or not
</script>

<Page>
	<svelte:fragment slot="header">
		<ListHeader
			listName={responseData.name}
			listDescription={responseData.description}
			listItems={responseData.items}
			listCreationDate={DateTime.fromISO(responseData.created_at)}
			{skeleton}
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		{#if success !== false}
			<!-- Iterate and add all items -->
			{#each responseData.items as listItem}
				<!-- An item can be two types: either a text type (heading and body) or an album
                (album data. We want to render different stuff depending on which one we currently have -->
				{#if listItem.type === 'album'}
					<AlbumCard data={listItem} cardType={'album_list_item'} {skeleton} />
				{:else if listItem.type === 'text'}
					<HeadingDivider title={listItem.heading} {skeleton}>
						<!-- Add body text if specified -->
						<svelte:fragment slot="heading">
							{#if listItem.body !== null && listItem.body.length > 0}
								<p>{listItem.body}</p>
							{/if}
						</svelte:fragment>
					</HeadingDivider>
				{/if}
			{/each}
		{:else}
			<Error description={`Kunde inte ladda in den efterfrågade listan. ${MANUAL_URLS_NOTICE}`} />
		{/if}
	</svelte:fragment>
</Page>
