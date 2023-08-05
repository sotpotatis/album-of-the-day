# Website

This subdirectory contains the website related to Album of the day. It contains a lot of stuff and a lot of magic!

## Backend (backend/)

The website backend uses Django and Django-REST to expose an API that can be used to retrieve metadata for everything.
The backend keeps track of the following things:

- Album of the day (Albums with comments and a date attached to them)
- Albums
- Artists
- Genres
- Album lists
- Spotify users (for a function where you can save albums to your Spotify account, also handled
  by the backend)

## Frontend (frontend/)

The website frontend exposes a static user interface that has been created using Svelte and Tailwind CSS.

## Installing

For installation instructions, see the Backend and Frontends own respective folders.

## Deploying and hosting

There are multiple ways to deploy the backend and the frontend.

The database is in my code at least hosted on Oracle Cloud (and is an Oracle Database)
and is not included in the hosting below.

## Dockerfiles

You can use the provided `docker-compose.yml` file to run the backend and frontend inside a Docker container.

### Publishing with Oketo

> **⚠️Please note:** The deployment with Okteto was only tested when this project
> was brand new, since I switched hosting provider. It will probably not work without modification.

The `okteto.yml` file is included with this repository, and you can deploy the frontend and backend to Okteto
with the following command:

`okteto deploy --build`
