<!-- SpotifyAuthenticationPopup.svelte
A popup that shows instructions and helps with authenticating with Spotify. -->
<script>
	import Popup from '../Generic/Popup.svelte';
	import Button from '../Generic/Button.svelte';
	import { createEventDispatcher, onMount } from 'svelte';
	import Icon from '../Generic/Icon.svelte';
	import { openURL } from '../../lib/utilities.js';
	import { BASE_URL } from '../../lib/apiClient.js';
	let STEPS = {
		INSTRUCTIONS: 1, // Shows how to authenticate with Spotify, invites the user to start the flow
		WAITING_FOR_AUTH: 2, // Authentication opened in another window.
		AUTH_COMPLETED: 3 // Authentication has completed
	};
	const STEP_VALUES = Object.values(STEPS);
	let currentStep = STEPS.INSTRUCTIONS;
	const dispatch = createEventDispatcher();
	const closePopup = () => {
		// Create a function for closing the popup
		dispatch('popupclose');
	};
	const nextStep = () => {
		// Create a function for going to the next step in the popup.
		const currentStepIndex = STEP_VALUES.indexOf(currentStep);
		if (currentStepIndex < STEP_VALUES.length - 1) {
			// If we have another step to show
			currentStep = STEP_VALUES[currentStepIndex + 1];
		} else {
			closePopup();
		}
	};
	const SPOTIFY_AUTH_URL = `${BASE_URL}/spotify/auth`;
	// Wait until authorized if relevant
	/**
	 * Checks if the user has been authenticated in Spotify by checking if the local storage
	 * authentication key exists.
	 * @param interval An interval that checks for authentication, so we can clear it once
	 * authentication has been detected.
	 */
	function checkIfAuthorized(interval) {
		if (Object.keys(localStorage).includes('spotify_token')) {
			console.log('Authenticated with Spotify detected. Moving on to next step...');
			clearInterval(interval);
			nextStep();
		}
	}
	/**
	 * Checks if it is relevant to check (the popup window matches the waiting for authentication
	 * step), and if it is relevant, queue a check for if the user has been authenticated 4 times
	 * per second.
	 */
	function waitForAuthorization() {
		if (currentStep === STEPS.WAITING_FOR_AUTH) {
			const interval = setInterval(() => {
				checkIfAuthorized(interval);
			}, 250);
		}
	}
	$: currentStep, waitForAuthorization();
</script>

{#if currentStep === STEPS.INSTRUCTIONS}
	<Popup
		title="Länka ditt Spotify-konto"
		description="Album of the day kommer automatiskt skapa en spellista med titeln “Album of the day: sparat” där sparade album kommer att läggas till."
		on:popupclose
	>
		<svelte:fragment slot="content">
			<Button
				text="Logga in med Spotify"
				backgroundColor="albumOfTheDay-text-foreground"
				textColor="white"
				buttonStyle="big"
				on:click={() => {
					openURL(SPOTIFY_AUTH_URL, true);
					nextStep();
				}}
			>
				<svelte:fragment slot="icon">
					<Icon name="mdi:spotify" color="white" />
				</svelte:fragment>
			</Button>
			<a href="/about" class="underline" target="_blank">Läs mer</a>
		</svelte:fragment>
	</Popup>
{:else if currentStep === STEPS.WAITING_FOR_AUTH}
	<Popup
		title="Väntar på autentisering..."
		description="Logga in med ditt Spotify-konto genom att godkänna inloggningen som öppnades i ett separat fönster."
		on:popupclose
	>
		<svelte:fragment slot="content">
			<p class="animate-spin">
				<Icon
					size="huge"
					name="ant-design:loading-outlined"
					color="albumOfTheDay-text-foreground"
				/>
			</p>
			<p class="text-sm">
				<b>Öppnades inget fönster?</b> Testa att klicka
				<a href={SPOTIFY_AUTH_URL} target="_blank" class="underline">här</a>.
			</p>
		</svelte:fragment>
	</Popup>
{:else if currentStep === STEPS.AUTH_COMPLETED}
	<Popup
		title="Autentisering klar!"
		description="Du är nu inloggad med Spotify och kan börja spara album."
		on:popupclose
	>
		<svelte:fragment slot="content">
			<p><button class="underline" on:click={closePopup}>Gå vidare</button></p>
		</svelte:fragment>
	</Popup>
{/if}
