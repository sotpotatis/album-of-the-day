/* utilities.js
Various other utilities that is used throughout the website. */
// Some constants: this one is related to the color of on-page badges
export const GENRE_BADGE_COLOR = 'lime';
export const ALBUM_OF_THE_DAY_BADGE_COLOR = 'turqoise';
export const ALBUM_BADGE_COLOR = 'yellow';
export const LIST_BADGE_COLOR = 'green';
export const DAILY_ROTATION_BADGE_COLOR = 'bronze';
export const TYPE_TO_BADGE_COLOR = {
	genre: GENRE_BADGE_COLOR,
	album_of_the_day: ALBUM_OF_THE_DAY_BADGE_COLOR,
	album: ALBUM_BADGE_COLOR,
	list: LIST_BADGE_COLOR,
	daily_rotation: DAILY_ROTATION_BADGE_COLOR
};
// URL for image to show when there is no album cover
export const NO_ALBUM_COVER_URL = '/album-cover-unavailable.png';
// Grid classes: how many items to render in a horizontal grid for different types
export const TYPE_TO_GRID_CLASSES = {
	album_of_the_day: 'grid lg:grid-cols-3 gap-x-3 gap-y-3',
	daily_rotation: 'grid grid-cols-2 lg:grid-cols-5 gap-x-3 gap-y-3',
	genre: 'grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-x-3 gap-y-3',
	artist: 'grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-x-3 gap-y-3'
};
TYPE_TO_GRID_CLASSES.album = TYPE_TO_GRID_CLASSES.album_of_the_day; // Mirror configuration as the card is almost identical
// A notice that is shown on error messages in case we encounter a 404 etc.
export const MANUAL_URLS_NOTICE =
	'Om du skrivit in länken manuellt, dubbelkolla den. Annars, testa att komma tillbaka senare.';
/**
 * When using Svelte routing, we have to have a +page.js function to pass on IDs from the
 * dynamic router. This function avoids the need to copy + paste :)
 * @param params Params as returned by the load() function on +page.js.
 * @return {{id}} A dictionary with one parameter containing the ID that was passed in the routing.
 */
export function passIdToPage({ params }) {
	return {
		id: params.id
	};
}

/**
 * First ensures that we actually need to generate
 * summary text from a longer text given the max length, then generates summary text given an input text.
 * @param inputText The input text to generate a summary from.
 * @param summaryMaxLength The maximum length of the summary.
 * @return {(boolean|*)[]|(boolean|string)[]} A list with the following entries: [<summary generated>, <summary text>].
 * If the input text is smaller or equal to the summaryMaxLength, the first value will return false and the input text will be returned
 * as the second. If not, the first value will be true and the later will be a summary text that is generated from the input text.
 */
export function generateSummaryText(inputText, summaryMaxLength) {
	// First: check if we need to generate a summary
	if (inputText.length <= summaryMaxLength) {
		// If we do not to generate a summary
		return [false, inputText];
	} else {
		// If we need to generate a summary
		let summary = '';
		let sentences = inputText.split('.'); // Split input to get sentences
		if (sentences.length > 0 && sentences[sentences.length - 1] === '') {
			// Remove the last item if it is empty
			sentences = sentences.slice(0, sentences.length - 1);
		}
		// If we do not get any sentences, split by character. This is not ideal,
		// but better than nothing and will most likely not occur unless the input
		// does not contain sentences (very unlikely) or that the max length is low
		// (also unlikely, because I know approximately what I will feed to this function :))
		if (sentences.length < 2) {
			sentences = inputText.split('');
		}
		// We would ideally want the summary to consist of whole sentences.
		// This function takes care of that!
		let i = 0;
		while (true) {
			const currentSentence = sentences[i];
			if (summary.length + 5 + currentSentence.length > summaryMaxLength) {
				break; // Break if the length is too long
			} else {
				summary += currentSentence; // Add the current sentence if we can
			}
			i++;
		}
		summary += '[...]';
		return [true, summary];
	}
}

/**
 * Function to open a URL.
 * @param url The URL to open.
 * @param newTab true to open in a new tab, false to open it in the same tab.
 */
export function openURL(url, newTab) {
	window.open(url, newTab ? '_blank' : '_self');
}

/**
 * Gets all albums from an album list data. Sorts out other types of item types, such as text items.
 * @param listData The list data.
 * @return {*} A list of all albums in the list.
 */
export function getAlbumsInList(listData) {
	return listData.items.filter((value) => value.type === undefined || value.type === 'album');
}
/**
 * Generates a list of album images from list data that can be passed to the <Image> component
 * to create a thumbnail for the list.
 * @param listData The list data.
 * @return {*[]} A list of image data to pass to the <Image> component.
 */
export function getFirstAvailableAlbumImagesInList(listData, type = 'album_list') {
	// Filter in the list so that we are left with all albums that have covers
	// and we have made sure we remove any types that are not albums
	const albumsWithCovers = getAlbumsInList(listData).filter((value) => {
		let album = null;
		if (type === 'album_list') {
			album = value.album;
		} else if (type === 'daily_rotation') {
			album = value;
		} else {
			throw new Error(
				`Unsupported album image type list type: ${type}. Must be one of: \"album_list\" or \"daily_rotation\".`
			);
		}
		return album.cover_url !== null && album.cover_url.length > 0;
	});
	// Convert to the format that the <Image> component wantes
	let images = [];
	for (const albumData of albumsWithCovers) {
		if (images.length === 3) {
			break;
		}
		// To be able to use both the "album_list" argument
		// and the "daily rotation" argument, we use
		// this check
		let albumDataToUse = albumData;
		if (type === 'album_list') {
			albumDataToUse = albumData.album;
		}
		images.push({
			source: albumDataToUse.cover_url,
			alt: `Albumomslag för ${albumDataToUse.name}`
		});
	}
	return images;
}

/**
 * Sorts input data and groups them by their first letter.
 * This allows things like sorting genres by their name etc.
 * @param items The items that should be grouped.
 * @param nameKey The key to retrieve the name or the other thing to get the first letter of
 * to do the grouping. Defaults to "name".
 * @return {{}} Items grouped by their first letter in the nameKey.
 */
export function groupItemsByName(items, nameKey = null) {
	if (nameKey === null) {
		nameKey = 'name';
	}
	// First, sort items
	const sortedItems = items.sort((a, b) =>
		a[nameKey].toLowerCase().localeCompare(b[nameKey].toLowerCase())
	);
	// Then, group them by letter
	let groupedItems = {};
	for (const item of sortedItems) {
		const itemFirstLetter = item[nameKey].charAt(0).toUpperCase();
		// Add letter to list if it doesn't exist
		if (groupedItems[itemFirstLetter] === undefined) {
			groupedItems[itemFirstLetter] = [];
		}
		groupedItems[itemFirstLetter].push(item); // Add item to sorted dictionary
	}
	return groupedItems;
}
