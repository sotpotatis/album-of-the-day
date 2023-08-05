import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/kit/vite';
/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			// This builds a Node server at server/
			out: 'server'
		})
	},
	preprocess: vitePreprocess()
};

export default config;
