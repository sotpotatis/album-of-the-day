/* font.js
Various utilities related to setting and getting the font family on the page. */
import Cookies from 'js-cookie';
export const VALID_FONT_FAMILIES = ['default', 'dyslexic'];
export const FONT_CHANGED_EVENT_NAME = 'fontchange'; // Event that can be dispatched when the font has changed

/**
 * Gets the current font family that is in use by the page. If it is not set,
 * this function also handles setting the font family.
 * @return {string} The font family in use by the page.
 */
export function getFontFamily() {
	let fontFamily = Cookies.get('font_family');
	if (fontFamily === undefined) {
		// Set font family for the first time
		Cookies.set('font_family', 'default');
		fontFamily = 'default';
	} else if (!VALID_FONT_FAMILIES.includes(fontFamily)) {
		console.warn(`Invalid font family cookie entered (${fontFamily})! Setting to default.`);
		Cookies.set('font_family', 'default');
		fontFamily = 'default';
	}
	console.log(`Page font family: ${fontFamily}`);
	return fontFamily;
}
/**
 * Update what font family the page should use.
 * @param familyName The family name to use. "default" for the default font or "dyslexic" to use the dyslexic font.
 */
export function setFontFamily(familyName) {
	// Validate the font family name
	if (!VALID_FONT_FAMILIES.includes(familyName)) {
		throw new Error('Invalid font family name: is not one of the accepted font family names.');
	}
	console.log(`Updating font family to ${familyName}...`);
	Cookies.set('font_family', familyName);
}
