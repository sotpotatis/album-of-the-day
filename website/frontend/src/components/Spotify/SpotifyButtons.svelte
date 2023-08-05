<!--  SpotifyButtons.svelte
Button that allows adding an album to Spotify and that handles all the states
and whatnot we have to handle. -->
<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import {
		BASE_URL,
		getAlbumSpotifyStatus,
		getSpotifyStatus,
		toggleAlbumOnSpotify
	} from '../../lib/apiClient.js';
	import Button from '../Generic/Button.svelte';
	import Error from '../Generic/Error.svelte';
	import Icon from '../Generic/Icon.svelte';
	import SpotifyAuthenticationPopup from './SpotifyAuthenticationPopup.svelte';
	import { openURL } from '../../lib/utilities.js';
	export let albumId; // The ID of the album to attach the button to.
	export let albumSpotifyUID; // The Spotify UID of the album.
	export let albumSpotifyTrackURIs;
	export let skeleton = false; // Whether to show a skeleton loader or not
	$: authPopupIsOpen = false;
	// Three possible states of the button
	const STATES = {
		loading_spotify_status: 1, // When we're still loading if the user has authenticated with Spotify or not
		album_spotify_uid_not_available: 2, // If the album's Spotify UID is not available
		user_not_authenticated: 3, // If the user is not authenticated with Spotify
		user_authenticated: 4, // If the user is authenticated with Spotify and the album can be added to their playlist
		album_added: 5, // If the album is added to the user's Spotify playlist
		album_removed: 6 // If the album is removed from the user's Spotify playlist.
	};
	// I learned across this project so I'm not dollarsigning everywhere but Svelte were right in their docs -
	// this is addicting!
	$: albumSpotifyUIDAvailable = albumSpotifyUID !== null && albumSpotifyUID.length > 0;
	$: state = albumSpotifyUIDAvailable
		? STATES.loading_spotify_status
		: STATES.album_spotify_uid_not_available;
	$: loading = false;
	$: error = false;
	let albumAddedToPlaylist = null;
	let savedSpotifyToken = null;
	let spotifyUserData = {}; // The user's Spotify data
	// Define some predefined button states
	const ADD_TO_SPOTIFY_BUTTON_LOADING = { icon: 'line-md:loading-loop', text: '' };
	const ADD_TO_SPOTIFY_BUTTON_ERROR = { icon: 'bxs:error', text: '' };
	const ADD_TO_SPOTIFY_BUTTON_ADD = { icon: 'ic:round-plus', text: 'Spara till Spotify' };
	const ADD_TO_SPOTIFY_BUTTON_REMOVE = {
		icon: 'material-symbols:check',
		text: 'Tillagd på Spotify'
	};
	let addToSpotifyButtonInformation = ADD_TO_SPOTIFY_BUTTON_LOADING;
	const getSpotifyUserData = () => {
		// Request data if we can/should
		loading = false;
		if (albumSpotifyUIDAvailable) {
			// If we should load the user's Spotify authentication status
			console.log('Getting Spotify token...');
			savedSpotifyToken = localStorage.getItem('spotify_token');
			if (savedSpotifyToken !== null) {
				loading = true;
				addToSpotifyButtonInformation = ADD_TO_SPOTIFY_BUTTON_LOADING;
				getSpotifyStatus(savedSpotifyToken).then((result) => {
					error = !result[0];
					let responseData = result[1];
					loading = false;
					if (!error) {
						spotifyUserData = responseData;
						// Decide what to do with the response.
						if (responseData.authenticated) {
							console.log('The current user is authenticated via Spotify.');
							state = STATES.user_authenticated;
							console.log('Checking if album is added to Spotify...');
							loading = true;
							addToSpotifyButtonInformation = ADD_TO_SPOTIFY_BUTTON_LOADING;
							getAlbumSpotifyStatus(albumId, savedSpotifyToken).then((result) => {
								loading = false;
								console.log('Got album Spotify status response back.');
								error = !result[0];
								responseData = result[1];
								if (!error) {
									albumAddedToPlaylist = responseData.is_added_to_playlist;
									console.log(
										albumAddedToPlaylist
											? 'The album is added to the playlist.'
											: 'The album is not added to the playlist.'
									);
									state = albumAddedToPlaylist ? STATES.album_added : STATES.album_removed;
									addToSpotifyButtonInformation =
										state === STATES.album_added
											? ADD_TO_SPOTIFY_BUTTON_REMOVE
											: ADD_TO_SPOTIFY_BUTTON_ADD;
								} else {
									console.warn('An error occurred when retrieving Spotify status for an album!');
									addToSpotifyButtonInformation = ADD_TO_SPOTIFY_BUTTON_ERROR;
								}
							});
						} else {
							console.warn(
								'The current user is not authenticated with Spotify (token does not exist on remote server).'
							);
							// Remove spotify_token from local storage, as it is invalid
							localStorage.removeItem('spotify_token');
							console.log('Previously saved Spotify token removed from local storage.');
							state = STATES.user_not_authenticated;
						}
					} else {
						console.warn('An error occurred when retrieving Spotify authentication status!');
					}
				});
			} else {
				console.log('The current user is not authenticated with Spotify (no token saved).');
				state = STATES.user_not_authenticated;
				addToSpotifyButtonInformation = ADD_TO_SPOTIFY_BUTTON_ADD;
			}
		} else {
			console.log(`No Spotify UID is available for this album. (${albumSpotifyUID})`);
		}
	};
	$: albumSpotifyUID, getSpotifyUserData();
</script>

{#if authPopupIsOpen}
	<SpotifyAuthenticationPopup
		on:popupclose={() => {
			authPopupIsOpen = false;
			getSpotifyUserData(); // Re-check if the user has been authenticated.
		}}
	/>
{/if}
<!-- If the album UID is available on Spotify, show Spotify-related buttons -->
{#if albumSpotifyUIDAvailable}
	<!-- Show button for viewing on Spotify -->
	<Button
		text="Visa på Spotify"
		on:click={!skeleton
			? () => {
					openURL(`https://open.spotify.com/album/${albumSpotifyUID}`, true);
			  }
			: null}
	>
		<svelte:fragment slot="icon">
			<Icon name="logos:spotify-icon" color="logos-spotify" size="small" />
		</svelte:fragment>
	</Button>
	<!-- Only show this button if we know what it should say -->
	{#if loading || state === STATES.user_not_authenticated || state === STATES.album_added || state === STATES.album_removed}
		<!-- Show button for adding or removing from Spotify -->
		<Button
			text={addToSpotifyButtonInformation.text}
			on:click={!skeleton && !loading
				? () => {
						if (state === STATES.user_not_authenticated) {
							console.log('Starting authentication with Spotify...');
							authPopupIsOpen = true;
						} else {
							console.log('Requesting API to toggle Spotify status...');
							loading = true;
							addToSpotifyButtonInformation = ADD_TO_SPOTIFY_BUTTON_LOADING;
							toggleAlbumOnSpotify([albumSpotifyTrackURIs[0]], savedSpotifyToken).then((result) => {
								loading = false;
								const responseData = result[1];
								error = !result[0] || responseData.status === 'error';
								if (!error) {
									const albumWasAdded = responseData.number_of_added_items > 0;
									console.log(`Succeeded to ${albumWasAdded ? 'add' : 'remove'} album on Spotify.`);
									state = albumWasAdded ? STATES.album_added : STATES.album_removed;
									addToSpotifyButtonInformation = albumWasAdded
										? ADD_TO_SPOTIFY_BUTTON_REMOVE
										: ADD_TO_SPOTIFY_BUTTON_ADD;
								} else {
									console.warn('Failed to toggle album status on Spotify!');
								}
							});
						}
				  }
				: null}
		>
			<svelte:fragment slot="icon">
				<Icon name={addToSpotifyButtonInformation.icon} color="black" size="small" />
			</svelte:fragment>
		</Button>
	{/if}
{/if}
{#if error}
	<Error
		size="small"
		color="white"
		description="Lägg till på Spotify är inte tillgängligt just nu på grund av ett okänt fel."
	/>
{/if}
