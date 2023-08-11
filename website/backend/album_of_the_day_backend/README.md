# Album of the day backend

Hello! This is the backend of the Album of the day project. You can read a lot more about it in the root directory (relative to this one).

Anyways, here are some installation instructions:

### Installing

1. Set up a database on Oracle Cloud or using Oracle Database (otherwise you'll have to tweak the code a little bit)
2. Set your environment variables - here is a complete list:
   > **Note**: If you're using `docker-compose`, you have to put these variables in the file `backend.env`.
   > For a local deployment, you can store them in a file called `.env`. 
   * `DJANGO_SECRET_KEY`: Django secret key. Set this to something unique and secret!
   * `DJANGO_DEBUG`: Set to `True` if you need the debug server, otherwise you can leave this unset because `False` is the default.
   * `DATABASE_USER`: Name of the database user.
   * `DATABASE_PASSWORD`: The password to access the database
   * `DATABASE_HOST`: The database host. Leave empty for use with Oracle cloud.
   * `DATABASE_PORT`: The database port. Leave empty for use with Oracle cloud.
   * `DATABASE_ENGINE`: The database backend to use, for example django.db.backends.oracle.
   * `ORACLE_DATABASE_CLIENT_PATH`: Path to where the Oracle Database to use is installed.
   * `ORACLE_DATABASE_WALLET_PATH`: Path to the Oracle database wallet to use when connecting.
   * `LAST_FM_API_KEY`: The Last.FM API key to use for Last.FM API-related requests.
   * `LAST_FM_USER_AGENT`: The user agent to use when requesting data from Last.FM.
   * `LAST_FM_USERNAME`: The Last.FM username to use for the "daily rotations" feature.
   * `SPOTIFY_CLIENT_ID`: The Spotify Client ID for use with API requests to Spotify.
   * `SPOTIFY_CLIENT_SECRET`: The Spotify client secret for use with API requests to Spotify.
   * `SPOTIFY_USER_AGENT`: The Spotify user agent to use with requests to Spotify.
   * `FRONTEND_BASE_URL`: The URL where the frontend is accessible at. Used for redirection to the frontend.
   * `BASE_URL`: The base URL of the API (backend).
   * `ALBUM_OF_THE_DAY_BOT_TOKEN`: Discord token for the Album of the day Discord bot.
   * `ALBUM_IMAGES_FONT_PATH`: The font path to the font to use on Album of the day images (recommended is Archivo Black)

**Some environmental variable notes for Oracle Cloud**
* Set these variables to custom paths if needed:
`ORACLE_DATABASE_CLIENT_PATH`="C:\\oracle\\instantclient_21_10" (on Windows, for example).
`ORACLE_DATABASE_WALLET_PATH`="<root-path>/.wallet"

* **Editing paths for connecting to Oracle Cloud**

* You probably also need to modify the `sqlnet.ora` file, specifically this line:
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="[...]")))
```
so that the `DIRECTORY=` part matches the directory where your wallet files are put.
See [this](https://blogs.oracle.com/opal/post/connecting-to-oracle-cloud-autonomous-database-with-django#connect) 
guide (see "Download and Setup the Oracle Database wallet files").
If you're using the production docker containers in production, also see [this](https://www.talkapex.com/2021/01/connecting-to-oracle-cloud-database-ora-28759-failure-to-open-file/) note.
* Set the `DATABASE_USER` to `ADMIN`
* Set `DATABASE_PASSWORD` to the admin user password (from Oracle Cloud).
* Set `DATABASE_NAME` to the `DSN` (connection string, the *syntax* looks like this: `(description= (retry_count=20)()...`
* Set `DATABASE_HOST` *and* `DATABASE_PORT` to an *empty* string (important step!)


_____
3. Install the requirements - `cd album_of_the_day_backend && poetry install`
4. You should now be able to run the server!

### Developing

After following the instructions above, you can run `cd album_of_the_day_backend/album_of_the_day_backend && poetry run manage.py`
to run a development server.

### Discord bot

There is a Discord bot located at the path `album_of_the_day_backend/album_of_the_day_backend/website/discord_bot`. It has the ability
to create new album of the days and manage lists at the time of this writing.

### Task runner

The website also has a set of tasks that should be run at different times. You'll find more information about
those at `album_of_the_day_backend/album_of_the_day_backend/website/tasks`.