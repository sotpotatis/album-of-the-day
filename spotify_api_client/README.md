# Spotify API Client

This is a Spotify API client that I wrote for doing the following things:

1. Handle authorization flow from Spotify (one-time flow: user logs in and you receive a refresh token).
2. Perform tasks related to a user: 
   * create playlists
   * read playlists
   * read user data
3. Perform non-user-related tasks:
   * search
   * get album details

> **Note:** Only the above mentioned API functions have been implemented. This project was created for my "Album of the day"
> project. For a more robust and thorough/complete solution, see the [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/) library.