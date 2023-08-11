# Frontend website

This directory contains the frontend UI that fetches data from the backend. The frontend shows the following:

- Album of the days
- Albums
- Artists
- Lists
- Genres
- Daily rotations

It also includes a search function.

### Installing

`yarn install` will do the trick!

For generating favicons, you can also install [Real Favicon Generator](https://realfavicongenerator.net/)'s CLI: `npm install -g real-favicon`

### Developing

`yarn run dev` will start a development server.

### Building

- Run `yarn run favicon` to update favicons if you have changed them.
- Then run, `yarn run build`.

#### Hosting

The build results will be output the directory `server/`.
The server can then be added and ran using `yarn node server`. Also see the `Dockerfile` inside this directory
that does just exactly what is described here: builds the script (not the favicon though, you're expected to do that as a developer!)
and then runs and exposes the built webserver using `yarn`.
