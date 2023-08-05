<!-- MenuItem.svelte
Contains a menu item -->
<script>
	export let url; // URL to open on click
	export let text; // Text to use
</script>

<li>
	<a
		class="text-6xl md:text-7xl font-black text-gray-700 underline underline-offset-8 decoration-gray-500"
		href={url}>{text}</a
	>
</li>
