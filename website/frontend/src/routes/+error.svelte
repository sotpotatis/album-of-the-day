<!-- +error.svelte
Error handler for 404-errors etc. -->
<script>
	import { page } from '$app/stores';
	import Page from '../components/Page.svelte';
	import HeaderTitle from '../components/Header/HeaderTitle.svelte';
	import { MANUAL_URLS_NOTICE } from '../lib/utilities.js';
	const STATUS_CODE_TO_ERROR_MESSAGE = {
		'404': {
			title: '404 - Sidan hittades inte',
			description: `Den efterfrågade sidan kunde inte hittas. ${MANUAL_URLS_NOTICE}`
		},
		'500': {
			title: '500 - Internt serverfel',
			description: `Tyvärr inträffade ett internt serverfel när denna sida skulle laddas in.
            Testa att komma tillbaka lite senare.`
		}
	};
	const statusCode = $page.status;
	let errorMessage = null;
	if (Object.keys(STATUS_CODE_TO_ERROR_MESSAGE).includes(statusCode.toString())) {
		errorMessage = STATUS_CODE_TO_ERROR_MESSAGE[statusCode.toString()];
	} else {
		console.warn(
			`Handling error that does not have an error message: status code is ${statusCode}.`
		);
		errorMessage = {
			title: `${statusCode} - Fel inträffade`,
			description: `Tyvärr inträffade ett fel på sidan.${
				$page.error.message !== undefined ? ` Felinformation: ${$page.error.message}` : ''
			}`
		};
	}
</script>

<Page fullScreenHeader={true}>
	<svelte:fragment slot="header">
		<div class="flex flex-col h-full items-center justify-center">
			<HeaderTitle title={errorMessage.title} description={errorMessage.description} />
		</div>
	</svelte:fragment>
</Page>
