<script>
	import Page from '../components/Page.svelte';
	import Statistics from '../components/Statistics/Statistics.svelte';
	import AlbumOfTheDayList from '../components/Lists/AlbumOfTheDayList.svelte';
	import HeaderTitle from '../components/Header/HeaderTitle.svelte';
</script>

<Page>
	<div slot="header">
		<HeaderTitle title="album of the day!" description="ett nytt album, varje dag!" />
	</div>
	<svelte:fragment slot="page">
		<Statistics />
		<AlbumOfTheDayList includeLatest={true} title="Fler album" />
	</svelte:fragment>
</Page>
