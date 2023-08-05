<!-- HeaderTitle.svelte
A title and description for the heading. -->
<script>
	export let title;
	export let description;
	export let skeleton = false; // Whether to show a skeleton loader or not
</script>

<h1 class={`text-5xl font-bold p-3${skeleton ? ' bg-white m-3' : ''}`}>
	{!skeleton ? title : 'Lorem ipsum'}
</h1>
<p class={`font-semibold${skeleton ? ' bg-white m-3' : ''}`}>
	{!skeleton ? description : 'Lorem ipsum dolor sit amet.'}
</p>
