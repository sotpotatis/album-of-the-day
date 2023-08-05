/** @type {import('tailwindcss').Config} */
// We want to make colors dynamically accessible, so we have to add them all to the list of classes not to purge
// The code for that continues below.
import colors from 'tailwindcss/colors.js';
// First we define some custom colors
const customColors = {
	logos: {
		lastFM: '#D01F3C',
		spotify: '#1ED760'
	},
	albumOfTheDay: {
		header: '#30457C', // Blue header color
		ruler: '#D2D2D2', // Color for <hr/> tags.
		text: {
			foreground: '#6B6B6B',
			background: '#939393', // Use for less emphasis
			menu: '#363636' // Used for the navigation menu
		},
		uiElements: {
			// Background colors for cards and other elements
			darkBackground: '#D9D9D9',
			lightBackground: '#F2F2F2'
		},
		badge: {
			// Colors used for badges and highlighting different types
			gray: '#BDBCBC',
			green: '#22C55E',
			lime: '#ABDB45',
			lime_2: '#90E87A',
			bronze: '#E5A972',
			turqoise: '#22BBC5',
			yellow: '#DACF6E'
		}
	}
};
// Create a list of all colors. Start with retrieving them from our custom colors
let allColorNames = [];
for (const [rootColorSchemeName, colorSchemeColors] of Object.entries(customColors)) {
	for (const [colorName, colorData] of Object.entries(colorSchemeColors)) {
		// As you can see above, colorData might be a string or a dictionary
		if (typeof colorData === 'string') {
			allColorNames.push(`${rootColorSchemeName}-${colorName}`);
		} else {
			// Handle the case where we have a dictionary
			for (const subColorName of Object.keys(colorData)) {
				allColorNames.push(`${rootColorSchemeName}-${colorName}-${subColorName}`);
			}
		}
	}
}
// ...add Tailwind defaults
for (const [colorName, colorWeights] of Object.entries(colors)) {
	// Not all colors have weights. The exceptions are defined below.
	if (!['white', 'black', 'base'].includes(colorName)) {
		// Add each color weight like 100, 200, ..., 900
		for (const colorWeight of Object.keys(colorWeights)) {
			allColorNames.push(`${colorName}-${colorWeight}`);
		}
	} else {
		allColorNames.push(`${colorName}`);
	}
}
//..then all the classes that we can apply colors on
let ignoreClasses = [];
for (const colorType of ['text', 'bg', 'ring', 'border', 'shadow']) {
	for (const colorName of allColorNames) {
		ignoreClasses.push(`${colorType}-${colorName}`);
	}
}
console.debug(`Created safelist including ${ignoreClasses.length} colors`);
export default {
	content: ['./src/**/*.{svelte,html,js,ts}'],
	safelist: ignoreClasses,
	theme: {
		extend: {
			colors: customColors,
			fontFamily: {
				default: ['Inter', 'sans-serif'],
				dyslexic: ['OpenDyslexicRegular']
			},
			animation: {
				spinAround: 'spinAround ease-in-out 500ms',
				grow: 'grow ease-in-out 1s forwards'
			},
			keyframes: {
				spinAround: {
					'0%': { transform: 'rotate(0deg)' },
					'100%': { transform: 'rotate(360deg)' }
				},
				grow: {
					'0%': { transform: 'scale(0)' },
					'100%': { transform: 'scale(1)' }
				}
			}
		}
	},
	plugins: []
};
