<!-- SpotifyAuthenticationStatusHeader.svelte
Header that shows after authenticating with Spotify. -->
<script>
	import HeaderTitle from './HeaderTitle.svelte';
	import Icon from '../Generic/Icon.svelte';
	export let spotifyAuthenticationStatus; // "success" or "error"
	export let spotifyAuthenticationErrorCode; // An error code, if any
	const ERROR_CODE_TO_ERROR_MESSAGE = {
		// Mapping: error code --> error message
		state_mismatch: 'Spotifys servrar returnerade ett fel (lägesmismatch). Försök igen senare.',
		spotify_error: 'Spotifys servrar returnerade ett fel. Försök igen senare.',
		missing_permissions:
			'Du klickade på "Avbryt" på bekräftelseskärmen på Spotify och inte på "Acceptera".'
	};
	$: error = spotifyAuthenticationStatus !== 'success';
</script>

<div class={`flex flex-col justify-center items-center${error ? ' h-full' : ''}`}>
	<Icon size="gigantic" name={error ? 'radix-icons:cross-2' : 'octicon:check-16'} />
	<HeaderTitle
		title={!error ? 'Autentisering klar!' : 'Autentisering misslyckades!'}
		description={!error
			? 'Du kan nu stänga denna sida. Kolla dina flikar för att hitta vart du var innan detta.'
			: `Ett fel uppstod. Anledning: ${ERROR_CODE_TO_ERROR_MESSAGE[spotifyAuthenticationErrorCode]}`}
	/>
</div>
