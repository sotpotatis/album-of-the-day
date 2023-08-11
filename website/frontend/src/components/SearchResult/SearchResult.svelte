<!-- SearchResult.svelte
The SearchResult component allows us to do a custom search for a predefined type of item
using provided filters and then display it inside a heading with a little count badge beside it. -->
<script>
	import {
		DUMMY_ALBUM_DATA,
		DUMMY_ALBUM_OF_THE_DAY_DATA,
		DUMMY_ARTIST_DATA,
		DUMMY_DAILY_ROTATION_DATA,
		DUMMY_GENRE_DATA,
		DUMMY_LIST_DATA
	} from '../../lib/dummyData.js';
	import { onMount } from 'svelte';
	import {
		getAlbumOfTheDays,
		getAlbums,
		getArtist,
		getArtists,
		getDailyRotations,
		getGenres,
		getLists
	} from '../../lib/apiClient.js';
	import HeadingDivider from '../Generic/HeadingDivider.svelte';
	import Badge from '../Generic/Badge.svelte';
	import AlbumCard from '../Card/Helpers/AlbumCard.svelte';
	import Error from '../Generic/Error.svelte';
	import { TYPE_TO_BADGE_COLOR, TYPE_TO_GRID_CLASSES } from '../../lib/utilities.js';
	import DailyRotationsCard from '../Card/Helpers/DailyRotationsCard.svelte';
	import ListCard from '../Card/Helpers/ListCard.svelte';
	import GenreTag from '../Genres/GenreTag.svelte';
	import Button from '../Generic/Button.svelte';
	import ArtistTag from '../Artists/ArtistTag.svelte';
	export let searchType; // Type to search: one of "genres", "album_of_the_days", "lists", or "daily_rotations"
	export let searchFilters; // An object including the filters to apply during the search.
	export let searchLimit = null; // Any limit to impose
	export let title = null; // An optional title
	export let inline = true; // Show inline or as a standalone card
	export let backgroundColor = 'white'; // Background color if inline is false.
	export let defaultCollapsed = false; // Optionally collapse by default
	const TYPE_TO_TITLE = {
		// Defaults unless title is not set
		genres: 'Genrer',
		artists: 'Artister',
		lists: 'Listor',
		album_of_the_days: 'Album of the day',
		albums: 'Album',
		daily_rotations: 'Dagliga rotationer'
	};
	$: titleToUse = title !== null ? title : TYPE_TO_TITLE[searchType];
	const TYPE_TO_DUMMY_DATA = {
		// Mappings --> Search type: dummy data
		genres: [
			DUMMY_GENRE_DATA,
			DUMMY_GENRE_DATA,
			DUMMY_GENRE_DATA,
			DUMMY_GENRE_DATA,
			DUMMY_GENRE_DATA
		],
		artists: [
			DUMMY_ARTIST_DATA,
			DUMMY_ARTIST_DATA,
			DUMMY_ARTIST_DATA,
			DUMMY_ARTIST_DATA,
			DUMMY_ARTIST_DATA
		],
		lists: [
			DUMMY_LIST_DATA,
			DUMMY_LIST_DATA,
			DUMMY_LIST_DATA,
			DUMMY_LIST_DATA,
			DUMMY_LIST_DATA,
			DUMMY_LIST_DATA
		],
		album_of_the_days: [
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA,
			DUMMY_ALBUM_OF_THE_DAY_DATA
		],
		albums: [
			DUMMY_ALBUM_DATA,
			DUMMY_ALBUM_DATA,
			DUMMY_ALBUM_DATA,
			DUMMY_ALBUM_DATA,
			DUMMY_ALBUM_DATA
		],
		daily_rotations: [
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA,
			DUMMY_DAILY_ROTATION_DATA
		]
	};
	const TYPE_TO_API_FUNCTION = {
		// Mappings: Search type --> API function
		genres: getGenres,
		artists: getArtists,
		lists: getLists,
		album_of_the_days: getAlbumOfTheDays,
		albums: getAlbums,
		daily_rotations: getDailyRotations
	};
	const TYPE_TO_GRID_CLASSES_SEARCH_RESULT = {
		// Custom defintion of what grid classes to use for the inline search results card
		album_of_the_day: 'grid grid-cols-1 lg:grid-cols-3 gap-x-3 gap-y-3',
		daily_rotation: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-x-3 gap-y-3',
		genre: 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-x-3 gap-y-3',
		artist: 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-x-3 gap-y-3'
	};
	TYPE_TO_GRID_CLASSES_SEARCH_RESULT.album = TYPE_TO_GRID_CLASSES_SEARCH_RESULT.album_of_the_day;
	const DEFAULT_RESULT_VALUE = [null, TYPE_TO_DUMMY_DATA[searchType]]; // success = null to show skeleton loader, and some dummy data
	let [success, responseData] = DEFAULT_RESULT_VALUE;
	let cachedResults = {};
	$: searchKey = `${JSON.stringify(searchFilters)}-${searchLimit}`; // Create a unique key for the search so we can cache it.
	const search = () => {
		if (!Object.keys(cachedResults).includes(searchKey)) {
			[success, responseData] = DEFAULT_RESULT_VALUE;
			// Each of the TYPE_TO_API_FUNCTION functions has the following arguments and in the following order:
			// limit, filters. Could be a bit cleaner to do this with kwargs but whatever.
			TYPE_TO_API_FUNCTION[searchType](searchLimit, searchFilters).then((result) => {
				[success, responseData] = result;
				if (success) {
					cachedResults[searchKey] = responseData;
				}
			});
		} else {
			[success, responseData] = [true, cachedResults[searchKey]]; // Load the cached result
		}
	};
	onMount(search);
	$: searchFilters, search();
	$: skeleton = success !== true;
	// Note: the slice below is to remove the plural form: genres -> genre, for example
	$: searchTypeSingular = searchType.slice(0, -1);
</script>

<div class={`${!inline ? ` bg-${backgroundColor} border-2 border-gray-400 rounded-lg` : ''}`}>
	<HeadingDivider
		title={titleToUse}
		collapsible={!skeleton}
		defaultCollapsed={success !== false ? defaultCollapsed : false}
	>
		<svelte:fragment slot="heading">
			<Badge
				color={TYPE_TO_BADGE_COLOR[searchTypeSingular]}
				text={responseData.length}
				{skeleton}
			/>
		</svelte:fragment>
		<svelte:fragment slot="collapsible">
			{#if success !== false}
				<div
					class={`${
						!inline
							? TYPE_TO_GRID_CLASSES_SEARCH_RESULT[searchTypeSingular]
							: TYPE_TO_GRID_CLASSES[searchTypeSingular]
					}${!inline ? ' p-3 md:p-8' : ''}`}
				>
					{#each responseData as itemData}
						<!-- Render each result depending on the thing that we are searching -->
						{#if searchType === 'album_of_the_days' || searchType === 'albums'}
							<AlbumCard
								data={itemData}
								{skeleton}
								compact={true}
								alwaysCompact={false}
								cardType={searchTypeSingular}
							/>
						{:else if searchType === 'daily_rotations'}
							<DailyRotationsCard data={itemData} {skeleton} />
						{:else if searchType === 'lists'}
							<ListCard data={itemData} {skeleton} />
						{:else if searchType === 'genres'}
							<GenreTag
								name={itemData.name}
								id={itemData.id}
								color={itemData.color}
								size="medium"
							/>
						{:else if searchType === 'artists'}
							<ArtistTag artistId={itemData.id} artistName={itemData.name} />
						{/if}
					{/each}
				</div>
			{:else}
				<Error
					description="Sorry, någonting gick fel i sökningen. Vänligen försök igen lite senare!"
				/>
			{/if}
		</svelte:fragment>
	</HeadingDivider>
</div>
