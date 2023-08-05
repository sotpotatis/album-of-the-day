/* apiClient.js
Creates an API client for use with the Album of the day backend. */
export const BASE_URL = import.meta.env.DEV
	? ' https://5af1-217-213-76-20.ngrok-free.app' // 'http://localhost:8000'
	: 'https://album-of-the-day-api.albins.website';
/**
 * Sends a request to the Album of the day backend API.
 * @param path The API path to request.
 * @param method The method to use.
 * @param jsonToPost null if you do not have any JSON to post, otherwise an Object with JSON data to include in the body
 * @param queryArguments Any URL query arguments to include
 * @param paginationFunction Used for endpoints that have pagination. Set a function that receives the request JSON and returns
 * a list that can be appended on to other data to paginate. Also receives any previous data stored by the server.
 * @param paginationLimit Maximum number of items to return.
 * @param previousEntries Internal parameter used for pagination. Previous data returned by paginationFunction.
 * @return {Promise<(boolean|Promise<any>)[]|boolean[]>} A list in the following format: [requestSucceeded, responseJSON].
 * Note: If requestSucceeded is false, then responseJSON might be null.
 */
export async function sendRequest(
	path,
	method,
	jsonToPost,
	queryArguments,
	paginationFunction,
	paginationLimit,
	previousEntries
) {
	// Construct and send the request
	let fetchOptions = {
		method: method
	};
	// Generate headers
	let headers = {
		Accept: 'application/json'
	};
	// Add headers for JSON if needed
	if (jsonToPost !== null) {
		headers['Content-Type'] = 'application/json';
		fetchOptions.body = JSON.stringify(jsonToPost);
	}
	// Add query arguments if needed/provided
	if (queryArguments == null) {
		queryArguments = {};
	}
	// We have to add the .page parameter to get a paginated response.
	if (paginationFunction !== null && queryArguments.page === undefined) {
		queryArguments.page = 1;
	}
	const searchParams =
		Object.keys(queryArguments).length > 0 ? `?${new URLSearchParams(queryArguments)}` : '';
	const rawRequestURL = `${BASE_URL}${path}`; // Request URL without search parameters
	const requestURL = `${rawRequestURL}${searchParams}`;
	fetchOptions.headers = headers; // Add headers
	let responseJSON = null;
	try {
		const response = await fetch(requestURL, fetchOptions);
		responseJSON = await response.json();
		console.log(`Response from server:`, responseJSON);
		if (response.status.toString().startsWith('2')) {
			// Check for pagination
			if (responseJSON.next !== undefined && responseJSON.next !== null) {
				console.debug(`Applying pagination to request ${requestURL}...`);
				// For pagination, the caller defines a function that returns us a list. This function will help us create a
				// list of data
				let responseData = paginationFunction(responseJSON, previousEntries);
				if (previousEntries !== undefined) {
					previousEntries.push(...responseData);
				} else {
					previousEntries = responseData;
				}
				// Resend the request as long as there is no limit blocking it
				if (
					paginationLimit === null ||
					paginationLimit === undefined ||
					paginationLimit < previousEntries.length
				) {
					queryArguments.page += 1;
					return await sendRequest(
						path,
						method,
						jsonToPost,
						queryArguments,
						paginationFunction,
						paginationLimit,
						previousEntries
					);
				}
			} else if (paginationFunction !== null) {
				// If there is no next page but a limit has been defined, ensure we get a list back
				const paginatedData = paginationFunction(responseJSON, previousEntries);
				// previousEntries might still be defined if the "next" parameter was applied before because of
				// pagination, but we are on the last page. So we have to check it here.
				if (previousEntries !== undefined) {
					previousEntries.push(...paginatedData);
				} else {
					previousEntries = paginatedData;
				}
				// And the list should have the correct length!
				if (
					paginationLimit !== null &&
					paginationLimit !== undefined &&
					previousEntries.length > paginationLimit
				) {
					previousEntries = previousEntries.slice(0, paginationLimit - 1);
				}
			}
			const dataToReturn = previousEntries === undefined ? responseJSON : previousEntries;
			console.log(`Returning data for a request to ${requestURL}:`, dataToReturn);
			return [true, dataToReturn];
		} else {
			throw new Error(`Request to server failed with unexpected status code ${response.status}`);
		}
	} catch (e) {
		console.warn(`Request to server failed! :(`, e);
		try {
			console.log(await response.text());
		} catch (e) {
			console.log('(response data not available)');
		}
		return [false, paginationFunction !== null && paginationFunction !== undefined ? [] : {}];
	}
}
/**
 * Since most of the requests to the API have the same format, this genericPaginationFunction can be used as a paginationFunction argument
 * for sendRequest. It returns everything under the "results" key in the API.
 * @param responseJSON The response JSON as received by the server.
 * @param previousEntries Any previous returns from this function. We use these because apparently, the function
 * in Django's apgination system that I am using does return data that might still be on the earlier page.
 * @return {*}
 */
function genericPaginationFunction(responseJSON, previousEntries) {
	let entries = [];
	const previousEntriesExist = previousEntries !== null && previousEntries !== undefined;
	if (!previousEntriesExist) {
		// Fill out empty data if not set
		previousEntries = [];
	}
	// This was quite nasty
	// But what I had to do was to check if two objects in an array were identical.
	// And this is what I came up with, because .indexOf nor .includes nor in didn't work
	const objectIsInArray = (object) => {
		return (input) => JSON.stringify(input) === JSON.stringify(object);
	};
	// Add data from this response
	for (const result of responseJSON.results) {
		// Validate that the result is not already in an array
		if (!previousEntries.some(objectIsInArray(result)) && !entries.some(objectIsInArray(result))) {
			entries.push(result);
		}
	}
	return entries;
}
// Filter functions
// Note: the API supports filtering over a couple of different items.
// The code below generates and defines code for interacting with filters
// Mappings: argument to the function --> URL parameter to request when filtering
const ALBUM_OF_THE_DAY_FILTER_PARAMETERS = {
	date: 'date',
	comments: 'comments',
	album_name: 'album__name',
	album_id: 'album__id',
	album_genres_name: 'album__genres__name',
	album_genres_id: 'album__genres__id',
	album_genres_description: 'album__genres__description',
	search: 'search'
};
const ALBUM_LIST_FILTER_PARAMETERS = {
	name: 'name',
	items_album_name: 'items__album__name',
	items_album_id: 'items__album__id',
	items_album_genres_name: 'items__album__genres__name',
	items_album_genres_id: 'items__album__genres__id',
	items_album_genres_description: 'items__album__genres__description',
	items_text: 'items__text',
	search: 'search'
};
const DAILY_ROTATION_FILTER_PARAMETERS = {
	name: 'name',
	day: 'day',
	description: 'description',
	genres_name: 'genres__name',
	genres_id: 'genres__id',
	genres_description: 'genres__description',
	albums_name: 'albums__name',
	albums_id: 'albums__id',
	albums_genres_name: 'albums__genres__name',
	albums_genres_id: 'albums__genres__id',
	albums_genres_description: 'albums__genres__description',
	search: 'search'
};
const GENRES_FILTER_PARAMETERS = {
	name: 'name',
	id: 'id',
	search: 'search'
};
const ALBUM_FILTER_PARAMETERS = {
	name: 'name',
	id: 'id',
	artists_name: 'artists__name',
	artists_id: 'artists__id',
	genres_name: 'genres__name',
	genres_id: 'genres__id',
	search: 'search'
};
const ARTIST_FILTER_PARAMETERS = {
	name: 'name',
	id: 'id',
	search: 'search'
};
/**
 * Generates query arguments to be used based on a provided filter(s).
 * @param filters The filters that should be applied as an object in the format {<parameter to filter>: <value to filter>}
 * @param filterParameters The filter parameters that are available. For example, the constant ALBUM_OF_THE_DAY_FILTER_PARAMETERS
 * or any of the other constants with a similar naming.
 * @param previousQueryArguments Pass any user-specified query arguments here to avoid them getting lost.
 * @return {Object} Query arguments with filter parameters included inside of them.
 */
function generateFilterQueryArguments(filters, filterParameters, previousQueryArguments = null) {
	let result = previousQueryArguments;
	if (result === null && filters.length > 0) {
		result = {};
	}
	// Generate all query arguments
	// filterId will be a key in one of the definitions above and filterValue will be the value to search/filter from
	for (const [filterId, filterValue] of Object.entries(filters)) {
		// Split the filter ID so the user can provide __exact, __gte, __lte etc. filters at the end of the value
		// This is not supported by all values, but the user will probably know this :)
		const filterIdParts = filterId.split('__');
		const filterRoot = filterIdParts[0];
		const filterIdExtras =
			filterIdParts.length > 1 ? '__' + filterIdParts.slice(1, filterId.length).join('__') : ''; // Add any extra parts such as __gte to the resulting filter key.
		result[filterParameters[filterRoot] + filterIdExtras] = filterValue; // Add filter to query arguments
	}
	return result;
}
/**
 * Gets album of the days.
 * @param limit The maximum number of album of the days to return.
 * @param filters The data for any filters to apply.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getAlbumOfTheDays(limit = null, filters = null) {
	console.log('Getting album of the day data from the API...');
	let queryArguments = {};
	if (filters !== null) {
		queryArguments = generateFilterQueryArguments(
			filters,
			ALBUM_OF_THE_DAY_FILTER_PARAMETERS,
			queryArguments
		);
	}
	return await sendRequest(
		'/api/album-of-the-days',
		'GET',
		null,
		queryArguments,
		genericPaginationFunction,
		limit
	);
}

/**
 * Retrieves all time statistics of models, i.e. how many of albums, genres etc. that are added on the server database
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getStatistics() {
	console.log('Getting statistics data from the API...');
	return await sendRequest('/api/statistics', 'GET', null, null, null, null);
}
/**
 * Retrieves an individual album of the day.
 * @param id The ID of the album of the day to retrieve.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getAlbumOfTheDay(id) {
	return await sendRequest(`/api/album-of-the-days/${id}`, 'GET', null, null, null, null);
}

/**
 * Gets all the available years and months for when a certain item is available for.
 * @param itemType The type of the item. ""album-of-the-days" to get album of the days,  "daily-rotations" to get daily rotations.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getAvailableMonths(itemType) {
	const VALID_ITEM_TYPES = ['album-of-the-days', 'daily-rotations']; // Valid values for itemType
	if (!VALID_ITEM_TYPES.includes(itemType)) {
		throw new Error(
			`Invalid argument passed to getAvailableMonths: must be one of ${VALID_ITEM_TYPES.join(',')}`
		);
	}
	return await sendRequest(`/api/${itemType}/available_months`, 'GET', null, null, null, null);
}

/**
 * Retrieves all genres (or all genres until the set limit) that is in the database.
 * @param limit If not null, set a limit for the maximum numbers of genres to retrieve.
 * @param filters The data for any filters to apply.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getGenres(limit = null, filters = null) {
	let queryArguments = {};
	if (limit !== null) {
		queryArguments.limit = limit;
	}
	if (filters !== null) {
		queryArguments = generateFilterQueryArguments(
			filters,
			GENRES_FILTER_PARAMETERS,
			queryArguments
		);
	}
	console.log(`Getting genre data from the API...`);
	return await sendRequest(
		`/api/genres`,
		'GET',
		null,
		queryArguments,
		genericPaginationFunction,
		limit
	);
}
/**
 * Get an individual genre by its ID.
 * @param id The ID of the genre.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getGenre(id) {
	return await sendRequest(`/api/genres/${id}`, 'GET', null, null, null, null);
}

/**
 * Gets all the lists that are stored in the database.
 * @param limit If not null, set a limit for the maximum numbers of lists to retrieve.
 * @param filters The data for any filters to apply.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getLists(limit = null, filters = null) {
	let queryArguments = {};
	if (limit !== null) {
		queryArguments.limit = limit;
	}
	if (filters !== null) {
		queryArguments = generateFilterQueryArguments(
			filters,
			ALBUM_LIST_FILTER_PARAMETERS,
			queryArguments
		);
	}
	return await sendRequest(
		`/api/lists`,
		'GET',
		null,
		queryArguments,
		genericPaginationFunction,
		null
	);
}

/**
 * Gets an individual list by its ID.
 * @param id The ID of the requested list.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getList(id) {
	return await sendRequest(`/api/lists/${id}`, 'GET', null, null, null, null);
}

/**
 * Get all the daily rotations that are stored in the database.
 * @param limit If not null, set a limit for the maximum numbers of daily rotations to retrieve.
 * @param filters The data for any filters to apply.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getDailyRotations(limit = null, filters = null) {
	// Generate query arguments
	let queryArguments = {};
	if (limit !== null) {
		// Add limit if provided
		queryArguments.limit = limit;
	}
	if (filters !== null) {
		// Add filters if provided
		queryArguments = generateFilterQueryArguments(
			filters,
			DAILY_ROTATION_FILTER_PARAMETERS,
			queryArguments
		);
	}
	return await sendRequest(
		`/api/daily-rotations`,
		'GET',
		null,
		queryArguments,
		genericPaginationFunction,
		limit
	);
}
/**
 * Get a single daily rotation by its ID.
 * @param id The ID of the daily rotation to retrieve.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getDailyRotation(id) {
	return await sendRequest(`/api/daily-rotations/${id}`, 'GET', null, null, null, null);
}

/**
 * Gets a list of all albums in the database.
 * @param limit If not null, set a limit for the maximum numbers of lists to retrieve.
 * @param filters The data for any filters to apply.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getAlbums(limit = null, filters = null) {
	// Generate query arguments
	let queryArguments = {};
	if (limit !== null) {
		// Add limit if provided
		queryArguments.limit = limit;
	}
	if (filters !== null) {
		// Add filters if provided
		queryArguments = generateFilterQueryArguments(filters, ALBUM_FILTER_PARAMETERS, queryArguments);
	}
	return await sendRequest(
		`/api/albums`,
		'GET',
		null,
		queryArguments,
		genericPaginationFunction,
		limit
	);
}

/**
 * Gets an individual album by its ID.
 * @param id The ID of the album to retrieve.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getAlbum(id) {
	return await sendRequest(`/api/albums/${id}`, 'GET', null, null, null, null);
}
/**
 * Get all the artists that are stored in the database.
 * @param limit If not null, set a limit for the maximum numbers of lists to retrieve.
 * @param filters The data for any filters to apply.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getArtists(limit = null, filters = null) {
	let queryArguments = {};
	if (limit !== null) {
		queryArguments.limit = limit;
	}
	if (filters !== null) {
		// Add filters if provided
		queryArguments = generateFilterQueryArguments(
			filters,
			ARTIST_FILTER_PARAMETERS,
			queryArguments
		);
	}
	return await sendRequest(
		`/api/artists`,
		'GET',
		null,
		queryArguments,
		genericPaginationFunction,
		limit
	);
}
/**
 * Get a single artist by its ID.
 * @param id The ID of the artist to retrieve.
 * @return {Promise<(boolean|Promise<*>)[]|boolean[]>}
 */
export async function getArtist(id) {
	return await sendRequest(`/api/artists/${id}`, 'GET', null, null, null, null);
}
// Spotify-related endpoints
// Note: the typical request flow for checking and potentially adding an album to a Spotify playlist is as follows:
// 1. Check local storage for "spotify_token" --> exists ? continue to step 2. || Abort.
// 2. Call getSpotifyStatus() with the value of the token
// 3. If authenticated --> continue to step 3 || Remove "spotify_token" from the local storage.
// 4. Get the status for the current album via getAlbumSpotifyStatus()
// 5. Is the album added to the user's playlist? If not, show a button that makes it possible to
// call getAlbumSpotifyStatus.
// Note that the Django API saves the token in your cookies, but the frontend does it in local storage
// to prevent a clashing if you're using the same URL for the frontend or backend (or if you are testing
// on localhost).
export async function getSpotifyStatus(storedToken) {
	const queryArguments = {
		// Pass the token as a query argument.
		spotify_token: storedToken
	};
	return await sendRequest(`/spotify`, 'GET', null, queryArguments, null, null);
}
export async function toggleAlbumOnSpotify(spotifyUIDs, storedToken) {
	if (typeof spotifyUIDs === 'string') {
		// Allow passing just one UID as a string
		spotifyUIDs = [spotifyUIDs];
	}
	const queryArguments = {
		items: spotifyUIDs.join(','), // Items are included in the "items" query parameter.
		spotify_token: storedToken
	};
	return await sendRequest(`/spotify/toggle`, 'POST', null, queryArguments, null, null);
}
export async function getAlbumSpotifyStatus(albumId, storedToken) {
	const queryArguments = {
		album_id: albumId, // Add the album ID to get the status from to the query
		spotify_token: storedToken
	};
	return await sendRequest(`/spotify/album/status`, 'GET', null, queryArguments, null, null);
}
