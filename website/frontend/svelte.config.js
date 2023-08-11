import nodeAdapter from '@sveltejs/adapter-node';
import netlifyAdapter from '@sveltejs/adapter-netlify';

import { vitePreprocess } from '@sveltejs/kit/vite';
// NOTE: The application supports multiple compatible kits based on environment variables:
// 1. "node" - build to a node server.
// 2: "netlify" - build to a Netlify server.
const kitConfigurations = {
	node: {
		adapter: nodeAdapter({
			// This builds a Node server at server/
			out: 'server'
		})
	},
	netlify: {
		adapter: netlifyAdapter({
			edge: true
		})
	}
};

// This is automatically detected below. (Netlify always has this environment variable set)
const isNetlify = process.env.NETLIFY === 'true';
/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: kitConfigurations[isNetlify ? 'netlify' : 'node'],
	preprocess: vitePreprocess()
};

export default config;
