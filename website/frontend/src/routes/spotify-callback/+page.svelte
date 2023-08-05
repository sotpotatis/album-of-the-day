<!-- Spotify callback
The authentication with Spotify is handled by the backend (the API).
It will redirect us to this page with some URL query parameters:
Like: status=success&username={spotify_user.username}&token={cookie_token
I thought you had to do this server-side with a JavaScript but Svelte provides it
for us. Awesome!
-->
<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import Page from '../../components/Page.svelte';
	import HeadingDivider from '../../components/Generic/HeadingDivider.svelte';
	import SpotifyAuthenticationStatusHeader from '../../components/Header/SpotifyAuthenticationStatusHeader.svelte';
	let status = null;
	let errorType = null;
	let userData = null; // Stores Spotify information on success
	if ($page.url.searchParams.has('status')) {
		status = $page.url.searchParams.get('status');
		if (status === 'success') {
			if ($page.url.searchParams.has('token') && $page.url.searchParams.has('username')) {
				console.log('The authentication succeeded. Storing token...');
				userData = {
					username: $page.url.searchParams.get('username'),
					spotify_token: $page.url.searchParams.get('token')
				};
				onMount(() => {
					localStorage.setItem('spotify_token', userData.spotify_token);
					console.log('Token stored.');
				});
			} else {
				// Just like with the check below, this is unexpected.
				console.warn('Unexpected: missing "token  or "user" argument.');
				status = 'error';
				errorType = 'argument_missing';
			}
		} else {
			console.warn('The authentication failed!');
			if ($page.url.searchParams.has('type')) {
				status = 'error';
				errorType = $page.url.searchParams.get('type');
			} else {
				console.warn('Unexpected: missing "type  or "user" argument.');
				status = 'error';
				errorType = 'argument_missing';
			}
		}
	} else {
		// This is unexpected. We should only get here if the user modified something manually.
		console.warn('Unexpected: missing "status argument.');
		status = 'error';
		errorType = 'argument_missing';
	}
	$: success = status === 'success';
</script>

<Page fullScreenHeader={!success}>
	<svelte:fragment slot="header">
		<SpotifyAuthenticationStatusHeader
			spotifyAuthenticationStatus={status}
			spotifyAuthenticationErrorCode={errorType}
		/>
	</svelte:fragment>
	<svelte:fragment slot="page">
		{#if success}
			<HeadingDivider title="Hur du sparar album" />
			<div class="text-left px-12">
				<ol
					class="list-decimal marker:text-4xl text-xl marker:font-black marker:italic flex flex-col gap-y-8"
				>
					<li>Navigera till sidan med albumet.</li>
					<li>
						Klicka på "Spara till Spotify"-knappen.<br />
						<span class="text-base">Det kan ta några sekunder för denna knapp att dyka upp.</span>
					</li>
					<li>Hitta alla sparade album på en och samma spellista på ditt Spotify.</li>
				</ol>
			</div>
		{/if}
	</svelte:fragment>
</Page>
