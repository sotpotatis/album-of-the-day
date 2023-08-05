/* dummyData.js
 * When implementing skeleton loaders, we need some dummy data to render.
 * This file provides that.*/
export const DUMMY_ARTIST_DATA = {
	id: 1,
	name: 'Example artist'
};
export const DUMMY_GENRE_DATA = {
	id: 1,
	name: 'example genre',
	description: 'Lorem Ipsum etc. etc.',
	description_source: null,
	album_count: 0,
	color: 'gray-600'
};
export const DUMMY_ALBUM_DATA = {
	id: 1,
	genres: [DUMMY_GENRE_DATA],
	artists: [DUMMY_ARTIST_DATA],
	name: 'Example album',
	cover_url: '',
	cover_source: 'last_fm',
	spotify_uid: '',
	spotify_track_uris: []
};
export const DUMMY_ALBUM_OF_THE_DAY_DATA = {
	id: 1,
	comments: '',
	date: '',
	album: DUMMY_ALBUM_DATA
};
export const DUMMY_LIST_DATA = {
	id: 1,
	items: [
		{
			// Dummy "text" type entry
			heading: 'Heading, lorem ipsum...',
			body: 'Ipsum lorem ipsum lorem lorem ipsum.',
			type: 'text'
		},
		{
			// Dummy "album" type entry.
			album: DUMMY_ALBUM_DATA,
			comments: 'Lorem ipsum dolor sit amet...',
			type: 'album'
		}
	],
	name: 'example list',
	description: 'Lorem ipsum dolor sit amet.'
};
export const DUMMY_DAILY_ROTATION_DATA = {
	id: 1,
	genres: [
		{
			id: 25,
			album_count: 1,
			name: 'indie rock',
			description: '',
			description_source: '',
			color: 'neutral-600'
		},
		{
			id: 27,
			album_count: 1,
			name: 'slowcore',
			description: '',
			description_source: '',
			color: 'sky-600'
		},
		{
			id: 28,
			album_count: 1,
			name: 'indie pop',
			description: '',
			description_source: '',
			color: 'violet-600'
		}
	],
	albums: [
		{
			id: 1,
			genres: [],
			artists: [
				{
					id: 1,
					name: 'Example artist'
				}
			],
			name: 'Example name',
			cover_url: '',
			cover_source: '',
			spotify_uid: ''
		}
	],
	day: '20XX-XX-XX',
	description: ''
};
