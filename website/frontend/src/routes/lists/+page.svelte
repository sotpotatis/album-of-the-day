<!-- Lists page
A page listing all the album lists that exists in the database.
-->
<script>
	import Page from '../../components/Page.svelte';
	import HeaderTitle from '../../components/Header/HeaderTitle.svelte';
	import HeadingDivider from '../../components/Generic/HeadingDivider.svelte';
	import ListList from '../../components/Lists/ListList.svelte';
</script>

<Page>
	<svelte:fragment slot="header">
		<HeaderTitle
			title="listor"
			description="här hittar du alla listor av album som jag har komponerat."
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		<HeadingDivider title="Listor" />
		<ListList />
	</svelte:fragment>
</Page>
