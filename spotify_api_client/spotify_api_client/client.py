"""client.py
Implements a Spotify API client."""
import base64
import datetime
import time
import urllib.parse, logging
from enum import Enum
from typing import Optional, Dict, List, Union, Callable

import requests

# Create global logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class SpotifyAPIException(Exception):
    """Generic API exception that is raised during unhandled errors."""
    pass

class SpotifyDataNotFound(Exception):
    """More specific exception compared to SpotifyAPIException that is specifically
    for 404-related errors."""
    pass

class SpotifyAuthenticationRevoked(Exception):
    """Exception if the Spotify authentication was revoked."""
    pass

class SpotifyTokenNeedsRefresh(Exception):
    """Exception on occasions like when the spotify token was passed
    but it has expired."""
    pass


class SpotifyScope(Enum):
    """Defines all possible scopes that can be requested when requesting authorization."""
    IMAGE_UPLOAD = "ugc-image-upload"
    READ_PLAYBACK_STATE = "user-read-playback-state"
    MODIFY_PLAYBACK_STATE = "user-modify-playback-state"
    READ_CURRENTLY_PLAYING = "user-read-currently-playing"
    APP_REMOTE_CONTROL = "app-remote-control"
    STREAMING = "streaming"
    READ_PRIVATE_PLAYLIST = "playlist-read-private"
    READ_COLLABORATE_PLAYLIST = "playlist-read-collaborative"
    MODIFY_PRIVATE_PLAYLIST = "playlist-modify-private"
    MODIFY_PUBLIC_PLAYLIST = "playlist-modify-public"
    MODIFY_FOLLOWED = "user-follow-modify"
    READ_FOLLOWED = "user-follow-read"
    READ_PLAYBACK_POSITION = "user-read-playback-position"
    READ_TOP_ARTISTS= "user-top-read"
    READ_RECENTLY_PLAYED = "user-read-recently-played"
    MODIFY_LIBRARY = "user-library-modify"
    READ_LIBRARY = "user-library-read"
    READ_EMAIL = "user-read-email"
    READ_PRIVATE_INFORMATION = "user-read-private"
    LINK_SOA = "user-soa-link"
    UNLINK_SOA = "user-soa-unlink"
    MANAGE_ENTITLEMENTS = "user-manage-entitlements"
    MANAGE_PARTNER = "user-manage-partner"
    CREATE_PARTNER = "user-create-partner"


def send_request(url:str, method:str, request_kwargs:Dict, token_refresh_function:Optional[Callable]=None)->Dict:
    """Global function for sending a request to the Spotify API.
    Handles rate limiting and returns the response JSON.

    :param url: The URL to request.

    :param method: The method to use.

    :param request_kwargs: Kwargs to pass to request.request function.

    :param token_refresh_function: Optional function to run if Spotify returns that the old token needs to be refreshed.
    Should be handled by other code but is a safeguard in extreme cases."""
    request_kwargs["url"] = url
    request_kwargs["method"] = method
    logger.info(f"Sending request to Spotify API with kwargs: {request_kwargs}...")
    response = requests.request(**request_kwargs)
    try:
        response_text = f"Response text: {response.text}"
    except Exception as e:
        response_text = f"Response text not available during to an exception ({e})"
    response_json = None
    try:
        response_json = response.json()
        logger.info(f"Spotify responded with JSON: {response_json} for a {method} request to {url}.")
    except Exception as e:
            raise SpotifyAPIException(f"Failed to parse response to JSON. {response_text}")
    if str(response.status_code).startswith("2"):
            return response_json
    elif response.status_code == 429:  # Handle rate limits
        if "Retry-After" not in response.headers:
            raise KeyError("Received rate limit error, but no Retry-After header from Spotify.")
        retry_after = int(response.headers["Retry-After"])
        logger.info(f"We were rate limited from Spotify... trying again in {retry_after}...")
        time.sleep(retry_after)
        return send_request(url=url, method=method, request_kwargs=request_kwargs, token_refresh_function=token_refresh_function)
    elif response.status_code == 404: # Handle 404
        raise SpotifyDataNotFound(f"Got a 404 from Spotify API: {response_text}")
    elif response.status_code == 400 and (response_json is not None and response_json.get("error_description", None) == "Refresh token revoked"):
        raise SpotifyAuthenticationRevoked("The user has revoked your authentication.")
    elif response.status_code == 401 and (response_json is not None and "error" in response_json and response_json["error"].get("message", None) == "The access token expired"):
        # Note: this might happen if the database contains an old key
        raise SpotifyTokenNeedsRefresh("You need to refresh the access token.")
    else:  # All status code not starting with 2xx are considered unexpected
        raise SpotifyAPIException(f"Unexpected status code from Spotify API: {response.status_code} {response_text}")

# Time-related utilities
def calculate_expires_in(seconds:int)->datetime.datetime:
    """Calculates a datetime for when the current token expires based on the number of seconds it expires in.

    :param seconds: The number of seconds that the token expires in."""
    return datetime.datetime.now() + datetime.timedelta(seconds=seconds)

def check_token_needs_refresh(expires_at: Optional[datetime.datetime], timestamp: Optional[datetime.datetime] = None)->int:
    """Checks if a token needs to be refreshed. Can also be used for any other datetime comparisons to compare
    two dates, but since we use it explicilty for tokens, we name it this way

    :param expires_at: A datetime when the token expires.

    :param timestamp: (Optional) A custom timestamp to compare to. Defaults to current datetime."""
    return expires_at is None or (datetime.datetime.now() if not timestamp else timestamp) >= expires_at

class SpotifyUser:
    """Allows access to user-related API views."""
    def __init__(self, access_token:str, expires_in:int, refresh_token:str, client_id:str, authorization_header:str, user_agent:str, on_token_refresh:Optional[Callable]=None, linked_database_id:Optional[int]=None):
        """Initializes a new, authenticated user.

        :param access_token: The access token that the user was authenticated with.

        :param expires_in: When the token expires, in seconds from now.

        :param refresh_token: The refresh token used to refresh credentials.

        :param client_id: The client ID of the app that the user was authenticated with.

        :param authorization_header self parameter from SpotifyClient, used for the authorization header

        :param user_agent Available as self parameter from SpotifyClient, used so Spotify can identify your requests.

        :param on_token_refresh: Optional function that runs when access tokens have been refreshed. It receives the new tokens
        and the current self state.

        :param linked_database_id: Optional parameter to store a database entry that this Spotify user is linked to. Made specifically
        for my "Album of the day" project.
        """
        # Create an internal logger
        self.logger = logging.getLogger(f"{__name__}:SpotifyUser")
        self.access_token = access_token
        self.expires_in = expires_in
        # Create "expires in" as a date
        self.expires_datetime = calculate_expires_in(self.expires_in)
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.authorization_header = authorization_header
        self.user_agent = user_agent
        self.on_token_refresh = on_token_refresh
        self.linked_database_id = linked_database_id
        # Get user information and add: it's so useful we do this on initialization
        self._user_information = self.get_me()
        self.username = self._user_information["display_name"]
        self.id = self._user_information["id"]

    def refresh_access_token(self):
        """Refreshes the user's access token."""
        self.logger.info("Sending request to refresh user access token...")
        response_json = send_request("https://accounts.spotify.com/api/token", "POST", {
            "data": {
        "grant_type": "refresh_token",
        "refresh_token": self.refresh_token,
        "client_id": self.client_id
        },
                "headers": {
            "Authorization": self.authorization_header,
            "User-Agent": self.user_agent
        }

            }, token_refresh_function=self.refresh_access_token)
        self.logger.info("Received new tokens for user.")
        if response_json["token_type"].lower() != "bearer":
            raise Exception(f"Unexpected token type returned from Spotify: {response_json['token_type'].lower()}")
        self.access_token = response_json["access_token"]
        self.expires_in = response_json["expires_in"]
        self.expires_datetime = calculate_expires_in(self.expires_in)
        self.logger.info("New token set and accessible.")
        if self.on_token_refresh is not None:
            self.logger.info("Calling on_token_refresh callback function...")
            self.on_token_refresh(self)
            self.logger.info("on_token_refresh function called.")
    def get_access_token(self)->str:
        """Gets a valid, refreshed access token to use for the user.
        If it needs refresh, we'll handle that!"""
        if check_token_needs_refresh(self.expires_datetime):
            self.logger.info("Refreshing access token for user...")
            self.refresh_access_token()
        return self.access_token # (if a refresh was needed, we would have gotten the token by now)

    def get_authorization_header(self)->str:
        """Similar to get_access_token, but returns the whole authorization header."""
        return f"Bearer {self.get_access_token()}"

    def get_me(self):
        """Gets details about the current user."""
        self.logger.info("Returning details about the current user...")
        request_data = {
                "headers": {
                "Authorization": self.get_authorization_header(),
                "User-Agent": self.user_agent
                }}
        try:
            response_json = send_request("https://api.spotify.com/v1/me", "GET", request_data)
        except SpotifyTokenNeedsRefresh:
            self.logger.warning("Refreshing Spotify access token for user...")
            self.refresh_access_token()
            return self.get_me()
        self.logger.info(f"Response JSON from server: {response_json}")
        return response_json

def base_64_string(input_string:str)->str:
    """Quick helper function to convert a value to a Base64 string.

    :param input_string: The value to convert.

    :returns input_string as a UTF-8 decoded base64 string."""
    return base64.b64encode(input_string.encode("UTF-8")).decode("UTF-8")

class ClientCredentials:
    def __init__(self, authorization_header:str, user_agent:str):
        """Creates an interface for the Client Credentials flow in Spotify, which is
        requests to non-user data.

        :param authorization_header: Self parameter of SpotifyClient. Header used for authorization

        :param user_agent: Self parameter of SpotifyClient. An user agent to use when requesting data. Used so Spotify can identify you.
        """
        # Save under client_authorization_header to avoid confusion with self.get_authorization_header()
        self.client_authorization_header = authorization_header
        self.user_agent = user_agent
        self.expires_datetime = None
        self.logger = logging.getLogger(f"{__name__}:ClientCredentials")

    def refresh_client_credentials(self):
        """Refreshes the client credentials for the user."""
        self.logger.info("Refreshing client credentials...")
        response_json = send_request("https://accounts.spotify.com/api/token", "POST", {
            "data": {
                "grant_type": "client_credentials"
            },
            "headers": {
                "Authorization": self.client_authorization_header,
                "User-Agent": self.user_agent
            }
        }, token_refresh_function=self.refresh_client_credentials)
        # Add access token and calculate when it expires.
        self.access_token = response_json['access_token']
        self.expires_in = response_json["expires_in"]
        self.expires_datetime = calculate_expires_in(self.expires_in)

    def get_access_token(self):
        """Uses the Client Credentials authentication method to get a Bearer token used for non-authorized requests.
        Ensure it is fresh and handles refreshes if needed!"""
        if check_token_needs_refresh(self.expires_datetime):
            self.logger.info("Refreshing client credentials...")
            self.refresh_client_credentials()
        return self.access_token
    
    def get_authorization_header(self)->str:
        """Similar to get_access_token, but returns the whole authorization header."""
        return f"Bearer {self.get_access_token()}"

class SpotifyClient:
    def __init__(self, client_id:str, client_secret:str, user_agent:str):
        """Initializes a Spotify API client instance.

        :param client_id: The client ID of the Spotify API app that you want to use.

        :param client_secret: The client secret of the Spotify API app that you want to use.

        :param user_agent: An user agent to use when requesting data. Used so Spotify can identify you."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        authorization_base64 = base_64_string(f'{client_id}:{client_secret}')
        self.authorization_header = f"Basic {authorization_base64}"
        self.logger = logging.getLogger(f"{__name__}:SpotifyClient")

    def send_request(self, url:str, method:str, request_kwargs:Dict, authorization:Optional[Union[SpotifyUser, ClientCredentials]]=None)->Dict:
        """Sends an authorized request to Spotify and parses and returns the result.

        :param url: The URL to request.

        :param method: The method to use, for example "GET"

        :param authorization: Pass a SpotifyUser object to authenticate as a Spotify user. Pass a ClientCredentials to authenticate using Spotify's
        client credentials flow.
        
        :param request_kwargs Any optional arguments to pass to requests.request.
        """
        if "headers" not in request_kwargs:
            request_kwargs["headers"] = {}
        # Decide what authorization token to use. If we should authenticate using a user,
        # we're using that access token. And if we're using client credentials flow,
        # we also want to use that!
        if authorization is not None:
            authorization_header = authorization.get_authorization_header() # (both SpotifyUser and ClientCredentials has this attribute!)
        else:
            authorization_header = self.authorization_header
        # Add what function to use when refreshing authorization.
        # This does differ between types so we handle that here
        authorization_refresh_function = None
        if authorization is not None:
            if isinstance(authorization, SpotifyUser):
                authorization_refresh_function = authorization.refresh_access_token
            else:
                authorization_refresh_function = authorization.refresh_client_credentials
        request_kwargs["headers"]["Authorization"] = f"{authorization_header}"
        request_kwargs["headers"]["User-Agent"] = self.user_agent
        # Send request and return the response. Logging etc. is handled by that function.
        try:
            return send_request(url, method, request_kwargs, authorization_refresh_function)
        except SpotifyTokenNeedsRefresh as e:
            # Handle the case where Spotify tokens need refreshing.
            # This function will handle that.
            logger.warning("Redoing request - my tokens are old...")
            if authorization_refresh_function is not None:
                authorization_refresh_function()  # Run the function to refresh tokens
                return self.send_request(url, method, request_kwargs, authorization)
            else:
                raise e
    def generate_user_authentication_url(self, redirect_uri:str, state:Optional[str]=None, scopes:Optional[List[SpotifyScope]]=None, show_dialog:Optional[bool]=None)->str:
        """Requests user authentication using the authorization code flow from Spotify (where the user visits
        a URL and grants permissions)

        :param redirect_uri: The redirect URI to redirect the user to after authentication

        :param state: An optional but recommeded parameter to avoid CSRF.

        :param scopes A list of scopes to request. If not set, will ask for everything.

        :param show_dialog: If True, Spotify will always display a user authentication prompt even if the user has authenticated.
        """
        query_strings = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
        }
        # Add optional parameters to URL.
        if scopes is not None:
            query_strings["scope"] = " ".join([scope.value for scope in scopes])
        if state is not None:
            query_strings["state"] = state
        if show_dialog is not None:
            query_strings["show_dialog"] = show_dialog
        return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(query_strings)}"

    def get_user_from_redirect(self, response_parameters:Dict, redirect_uri:str, state:Optional[str]=None)->SpotifyUser:
        """Retrieves an access token and creates a Spotify user from a redirect to the redirect_uri.

        :param response_parameters: The URL query parameters that were passed to the response.

        :param redirect_uri: The same redirect URI that was provided when constructing the authorization

        :param state: Can be used to protect against CSRF. If so, is provided in the initial token request."""
        if state is not None and response_parameters["state"] != state:
            raise SpotifyAPIException(f"State mismatch: {state}!={response_parameters['state']}")
        if "error" in response_parameters:
            raise SpotifyAPIException(f"Access token not available: the error {response_parameters['error']} occurred.")
        else:
            self.logger.info("Redirect response seems valid. Retrieving access token from redirect.")
            request_body = {
                "grant_type": "authorization_code",
                "code": response_parameters["code"],
                "redirect_uri": redirect_uri
            }
            response_json = self.send_request("https://accounts.spotify.com/api/token", "POST", {"data": request_body})
            if response_json["token_type"] != "bearer": # Value is always "Bearer"
                return SpotifyUser(
                    access_token=response_json["access_token"],
                    expires_in=response_json["expires_in"],
                    refresh_token=response_json["refresh_token"],
                    client_id=self.client_id,
                    authorization_header=self.authorization_header,
                    user_agent=self.user_agent
                )
            else:
                raise SpotifyAPIException(f"Unexpected token type: {response_json['token_type']}")

    def get_user_playlists(self, user:SpotifyUser, previous_playlists:List=Optional[None], next_url:Optional[str]=None)->List[Dict]:
        """Gets a list of playlists owned by a user.

        :param user: The user to retrieve all playlists for.

        :param previous_playlists: Value used for recursion.

        :param next_url: Used for recursion. Sets the URL to use for retrieving the next page with items."""
        self.logger.info("Retrieving user playlists...")
        if previous_playlists is not None:
            playlists = []
        else:
            playlists = previous_playlists
        # Use next page URL if specified
        if next_url is not None:
            url_to_use = next_url
        else:
            url_to_use = f"https://api.spotify.com/v1/users/{user.id}/playlists"
        response = self.send_request(url_to_use, "GET", {
            "json": {
                "limit": 50
            }
        }, authorization=user)
        if "next" in response and response["next"]:
            self.logger.info(f"Retrieved playlist page. Getting next...")
            playlists.extend(response["items"])
            return self.get_user_playlists(user, playlists,  response["next"])
        self.logger.info("No other playlist pages to retrieve. Returning playlists...")
        return playlists

    def get_user_playlist(self, user:SpotifyUser, playlist_id:str):
        """Gets a user's playlist.
        NOTE: See get_user_playlist_items for a function to get the items in the playlists!

        :param user: The user that owns the playlist.

        :param playlist_id: The owner of the playlist."""
        self.logger.info(f"Getting playlist {playlist_id}...")
        return self.send_request(f"https://api.spotify.com/v1/playlists/{playlist_id}", "GET", {}, authorization=user)

    def get_user_playlist_items(self, user:SpotifyUser, playlist_id:str, limit:Optional[int]=None, previous_items:Optional[List[Dict]]=None, next_url:Optional[str]=None):
        """Gets a user playlist.

        :param user: The user that owns the playlist.

        :param playlist_id: The owner of the playlist.

        :param limit: (Optional) Pass a custom limit.

        :param previous_items: Used for recursion. Do not provide, internal value.

        :param next_url: Used for recursion. Sets the URL to use for retrieving the next page with items."""
        self.logger.info(f"Getting items for playlist {playlist_id}...")
        if limit is None:
            limit = 50 # Default, the biggest
        if previous_items is None:
            playlist_items = []
        else:
            playlist_items = previous_items
        # Use next page URL if specified
        if next_url is not None:
            url_to_use = next_url
        else:
            url_to_use = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        response_json = self.send_request(url_to_use, "GET", {
            "params": {"limit": limit}
        }, authorization=user)
        playlist_items.extend(response_json["items"])
        if response_json["next"] and response_json["next"] is not None:
            logger.info(f"More tracks to retrieve from playlist {playlist_items}. Retrieving next page of tracks...")
            self.get_user_playlist_items(user, playlist_id, limit, playlist_items, response_json["next"])
        return playlist_items

    def create_playlist(self, user:SpotifyUser, name:str, public:Optional[bool]=None, collaborative:Optional[bool]=None, description:Optional[str]=None):
        """Creates a playlist for a user.

        :param user: The user that you want to create the playlist for.

        :param name: The name of the playlist.

        :param public: (Optional) Whether you want to make the playlist public or not.

        :param collaborative: (Optional) Whether you want to make the playlist collaborative or not.

        :param description: (Optional) A description of the playlist."""
        self.logger.info("Creating playlist...")
        request_body = {
            "name": name
        }
        # Add optional parameters
        if public is not None:
            request_body["public"] = public
        if collaborative is not None:
            request_body["collaborative"] = collaborative
        if description is not None:
            request_body["description"] = description
        return self.send_request(f"https://api.spotify.com/v1/users/{user.id}/playlists", "POST", {
            "json": request_body}, authorization=user) # The new playlist will be directly in the body

    def add_items_to_playlist(self, user:SpotifyUser, playlist_id:str, uris_to_insert:List[str],position:Optional[int]=None):
        """Allows you to add items to a playlist.

        :param user: The user that the playlist belongs to.

        :param playlist_id: The playlist ID to add items to.

        :param uris_to_insert: Any URIs to add to the playlist.

        :param position: (Optional) The position to insert the tracks on."""
        self.logger.info(f"Adding items to a playlist {playlist_id}...")
        request_body = {
            "uris": uris_to_insert
        }
        # Add additional parameters
        if position is not None:
            request_body["position"] = position
        return self.send_request(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", "POST", {"json": request_body}, authorization=user)

    def remove_items_from_playlist(self, user:SpotifyUser, playlist_id:str, uris_to_remove:List[str]):
        """Allows you to remove items to a playlist.

        :param user: The user that the playlist belongs to.

        :param playlist_id: The playlist ID to add items to.

        :param uris_to_insert: Any URIs to remove from the playlist."""
        self.logger.info(f"Adding items to a playlist {playlist_id}...")
        request_body = {
            "tracks": [
                {
                    "uri": uri_to_remove
                }
                for uri_to_remove in uris_to_remove
            ]
        }
        return self.send_request(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", "DELETE", {"json": request_body}, authorization=user)

    def get_album_tracklist(self, credentials:Union[ClientCredentials, SpotifyUser], album_uid:str, market:Optional[str]=None, limit:Optional[int]=None, previous_items:Optional[List[Dict]]=None, next_url:Optional[str]=None):
        """Allows you to get the tracklist for an album.

        :param client_credentials: An instance of ClientCredentials or SpotifyUser to use for authentication. Note: If you do not provide a user,
        you have to provide a value for the market kwarg! Otherwise the material will be returned as unavailable.

        :param album_uid: The album UID.

        :param market: Set the market that the API should check if the tracks are available in.

        :param limit: Pass a custom limit.

        :param previous_items: Used for recursion. Stores the items that previously has been retrieved from the server
        in earlier requests (when more requests are used).

        :param next_url: Used for recursion. Sets the URL to use for retrieving the next page with items.
        """
        if isinstance(credentials, ClientCredentials) and market is None:
            raise ValueError("You have to provide a value for the \"market\" key if you're authenticating without a user credential. Otherwise, Spotify will consider the material as unavailable.")
        # Add defaults
        if previous_items is None:
            previous_items = []
        if limit is None:
            limit = 50 # This is the biggest allowed limit according to the Spotify documentation
        request_body = {
            "limit": 50
        }
        if market is not None: # Add market to request body if specified
            request_body["market"] = market
        # Use next page URL if specified
        if next_url is not None:
            url_to_use = next_url
        else:
            url_to_use = f"https://api.spotify.com/v1/albums/{album_uid}/tracks"
        response = self.send_request(url_to_use, "GET", {"params": request_body}, authorization=credentials)
        previous_items.extend(response["items"])
        if response["next"] is not None: # Apply pagination if needed
            logger.debug(f"Applying pagination for album {album_uid} tracks.")
            return self.get_album_tracklist(
                credentials=credentials, album_uid=album_uid, limit=limit,
                previous_items=previous_items, next_url=next_url
            )
        return previous_items

    def search(self, client_credentials:ClientCredentials, query:str, type:Optional[str]=None, market:Optional[str]=None, limit:Optional[int]=None, previous_items:Optional[List[Dict]]=None, next_url:Optional[str]=None):
        """Allows you to search for items.

        :param client_credentials: An instance of ClientCredentials to use for authentication.

        :param query: The search query. For example, artist:Test

        :param type: Narrow down results by applying type filters such as "album" which will only return albums.

        :param market: Filter by market.

        :param limit: Pass a custom limit.

        :param previous_items: Used for recursion. Stores the items that previously has been retrieved from the server
        in earlier requests (when more requests are used).

        :param next_url: Used for recursion. Sets the URL to use for retrieving the next page with items.
        """
        self.logger.info("Searching Spotify...")
        request_body = {
            "q": query
        }
        # Add optional parameters
        if type is not None:
            request_body["type"] = type
        if market is not None:
            request_body["market"] = market
        if limit is not None:
            request_body["limit"] = limit
        # Use next page URL if specified
        if next_url is not None:
            url_to_use = next_url
        else:
            url_to_use = f"https://api.spotify.com/v1/search"
        response = self.send_request(url_to_use, "GET", {"params": request_body}, authorization=client_credentials)
        # Handle pagination
        if previous_items is None:
            results = []
        else:
            results = previous_items
        # The response will contain keys like this: {"albums": ..., "playlists": ...}. Handle them
        for result_type, result_type_data in response.items():
            results.extend(result_type_data["items"])
        if "next" in response and response["next"] is not None:
            self.logger.info("Applying pagination for a search...")
            return self.search(
                client_credentials=client_credentials, query=query, type=type, market=market, limit=limit, previous_items=results, next_url=response["next"]
            )
        if len(results) == 0:
            raise SpotifyDataNotFound(f"No results were found for search \"{query}\".")
        return results