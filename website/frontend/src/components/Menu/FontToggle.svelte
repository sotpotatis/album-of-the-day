<!-- FontToggle.svelte
Changes the font used on the page. -->
<script>
	import Icon from '../Generic/Icon.svelte';
	import { getFontFamily, setFontFamily, FONT_CHANGED_EVENT_NAME } from '../../lib/font.js';
	import { createEventDispatcher } from 'svelte';
	// Decide what colors, text and icon
	let fontFamily = getFontFamily();
	let dyslexiaFontEnabled = fontFamily === 'dyslexic';
	// Create event dispatcher for telling body when the font has changed
	const dispatch = createEventDispatcher();
</script>

<button
	class="flex flex-row gap-x-2 items-center"
	on:click={() => {
		fontFamily = dyslexiaFontEnabled ? 'default' : 'dyslexic';
		dyslexiaFontEnabled = !dyslexiaFontEnabled;
		setFontFamily(fontFamily);
		dispatch(FONT_CHANGED_EVENT_NAME, {});
	}}
>
	<Icon
		name={dyslexiaFontEnabled ? 'material-symbols:toggle-on' : 'material-symbols:toggle-off'}
		color={dyslexiaFontEnabled ? 'green-400' : 'gray-700'}
		size="medium"
	/>
	<span class="text-gray-700">Dyslexi-typsnitt</span>
</button>
