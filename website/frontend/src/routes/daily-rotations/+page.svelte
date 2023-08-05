<!-- Daily rotations page
Page that lists all the daily rotations. -->
<script>
	import HeaderTitle from '../../components/Header/HeaderTitle.svelte';
	import Page from '../../components/Page.svelte';
	import DailyRotationsList from '../../components/Lists/DailyRotationsList.svelte';
</script>

<Page>
	<svelte:fragment slot="header">
		<HeaderTitle
			title="dagliga rotationer"
			description="Vad lyssnar jag egentligen på? Denna sida har svaret! Här kan du dag för dag se vilka album och genrer som jag har lyssnat på. Nya dagliga rotationer skapas automatiskt i slutet av dagen."
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		<DailyRotationsList />
	</svelte:fragment>
</Page>
