<!-- Daily rotation page
Shows details about a daily rotation.
-->
<script>
	import { DUMMY_DAILY_ROTATION_DATA } from '../../../lib/dummyData.js';
	import { onMount } from 'svelte';
	import { getDailyRotation } from '../../../lib/apiClient.js';
	import Page from '../../../components/Page.svelte';
	import DailyRotationHeader from '../../../components/Header/DailyRotationHeader.svelte';
	import { DateTime } from 'luxon';
	import HeadingDivider from '../../../components/Generic/HeadingDivider.svelte';
	import Badge from '../../../components/Generic/Badge.svelte';
	import { MANUAL_URLS_NOTICE, TYPE_TO_BADGE_COLOR } from '../../../lib/utilities.js';
	import AlbumCard from '../../../components/Card/Helpers/AlbumCard.svelte';
	import GenreTag from '../../../components/Genres/GenreTag.svelte';
	import Error from '../../../components/Generic/Error.svelte';
	export let data; // Data containing URL parameters etc.
	let [success, responseData] = [null, DUMMY_DAILY_ROTATION_DATA]; // success = null to indicate skeleton loader, rest is dummy data
	$: dailyRotationId = data.id;
	onMount(() => {
		getDailyRotation(dailyRotationId).then((result) => {
			[success, responseData] = result;
		});
	});
	$: skeleton = success !== true; // Whether to show skeleton loader or not
</script>

<Page>
	<svelte:fragment slot="header">
		<DailyRotationHeader
			dailyRotationDate={DateTime.fromISO(responseData.day)}
			dailyRotationGenres={responseData.genres}
			dailyRotationAlbums={responseData.albums}
			{skeleton}
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		<HeadingDivider title="Album">
			<svelte:fragment slot="heading">
				<Badge text={responseData.albums.length} color={TYPE_TO_BADGE_COLOR.album} {skeleton} />
			</svelte:fragment>
		</HeadingDivider>
		{#if success !== false}
			{#each responseData.albums as albumData}
				<AlbumCard data={albumData} cardType="album" {skeleton}>
					<!-- Extend the card and include genre tags for each album -->
					<svelte:fragment slot="body">
						<div class="grid grid-cols-5">
							{#each albumData.genres as genreData}
								<GenreTag
									id={genreData.id}
									name={genreData.name}
									color={genreData.color}
									{skeleton}
									size="smaller"
									borderStyle="pill"
								/>
							{/each}
						</div>
					</svelte:fragment>
				</AlbumCard>
			{/each}
		{:else}
			<Error
				description={`Misslyckades att ladda in efterfrågad dagliga rotation. ${MANUAL_URLS_NOTICE}`}
			/>
		{/if}
	</svelte:fragment>
</Page>
