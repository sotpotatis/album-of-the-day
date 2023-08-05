import logging
from typing import Callable, Union
from .models import *

import requests

logging.basicConfig(level=logging.DEBUG)
# Define a custom exception class for API-related errors
class LastFMClientError(Exception):
    pass


# ...and for 404s
class LastFMDataNotFound(Exception):
    pass


class Client:
    def __init__(self, api_key: str, user_agent: str, base_url: Optional[str] = None):
        """initializes an API client.

        :param api_key The Last.FM API key to use.

        :param user_agent An identificable user agent. Wanted by the Last.FM API:
        "Please use an identifiable User-Agent header on all requests. This helps our logging and reduces the risk of you getting banned."."""
        self.api_key = api_key
        self.user_agent = user_agent
        self.logger = logging.getLogger(__name__)
        if base_url is None:
            base_url = "https://ws.audioscrobbler.com/2.0"
        else:
            base_url = base_url.strip("/")
        self.base_url = base_url

    def generate_request_kwargs(
        self,
        api_method: str,
        request_parameters: Optional[Dict] = None,
        request_method: Optional[str] = None,
    ) -> Dict:
        """Last.FM uses URL parameters to add request data. This function builds a request containing
        that.

        :param api_method The Last.FM method to access, for example user.getRecentTracks.

        :param request_parameters: The parameters to include in the request (URL parameters). (This function adds format, method (api_method)
        and API key methods automagically)

        :param request_method: Optional argument to send any other request than a GET request. At least most endpoints in the API use GET
        request methods."""
        if request_parameters is None:
            request_parameters = {}
        if request_method is None:
            request_method = "GET"
        # Add API key, method and format
        request_parameters["method"] = api_method
        request_parameters["api_key"] = self.api_key
        request_parameters["format"] = "json"
        # Generate final kwargs to pass to requests.Request
        request_kwargs = {
            "url": self.base_url,
            "params": request_parameters,
            "method": request_method,
            "headers": {"User-Agent": self.user_agent},
        }
        self.logger.debug(
            f"Generated request parameters for a request to {api_method}: {request_kwargs}."
        )
        return request_kwargs

    def send_request(
        self,
        api_method: str,
        request_parameters: Optional[Dict] = None,
        request_method: Optional[str] = None,
    ) -> Union[
        GetAlbumDetailsResponse,
        GetArtistResponse,
        GetTagInfoResponse,
        GetRecentTracksResponse,
    ]:
        """Sends a Last.FM request and handles the response.

        :param api_method The Last.FM method to access, for example user.getRecentTracks.

        :param request_parameters: The parameters to include in the request (URL parameters). (This function adds format, method (api_method)
        and API key methods automagically)

        :param request_method: Optional argument to send any other request than a GET request. At least most endpoints in the API use GET
        request methods.
        """
        self.logger.debug(f"Sending a Last.FM request to {api_method}...")
        # Prepare request
        request_kwargs = self.generate_request_kwargs(
            api_method, request_parameters, request_method
        )
        self.logger.debug("Sending a request...")
        response = requests.request(**request_kwargs)
        if response.status_code == 200:
            try:
                response_json = response.json()
                self.logger.debug(f"Last.FM responsed with JSON: {response_json}")
                return METHOD_TO_MODEL[api_method].parse_obj(
                    response_json
                )  # Return the response
            except Exception as e:
                error_message = (
                    f"Failed to decode response JSON. Original exception: {e}"
                )
                self.logger.critical(error_message, exc_info=True)
                raise LastFMClientError(error_message)
        elif response.status_code == 404:
            raise LastFMDataNotFound("The Last.FM server responded with 404.")
        else:
            error_message = f"Unexpected status code returned from the Last.FM API: {response.status_code}. Please look into changing request parameters etc."
            self.logger.critical(error_message)
            raise LastFMClientError(error_message)

    def handle_pagination(
        self,
        page_number,
        request_next: Callable,
        get_total_page_number: Callable,
        expand_response: Callable,
        previous_content=None,
    ):
        """A pagination handler. Will request an API method and keep adding data if there is more to it.

        :param page_number: The page number to retrieve.

        :param request_next: A function that will re-run the same request but with a new page number.
        This function receives a parameter: foo(new_page_number) and should return the response in the applicable model.

        :param get_total_page_number: A function to return the biggest page number based on a response. It receives
        bar(response) and should return the biggest page number

        :param expand_response: A function that takes a Last.FM response and adds it to wherever
        the pagination applies. This is because sometimes it's subkeys we are paginating. Gets called like:
        baz(<previous content>, <new_content>). NOTE: will receive None on the first call!

        :param previous_content: None on the first call, <data model with list inside> on subsequent calls"""
        self.logger.debug(f"Getting page: {page_number}...")
        response = request_next(page_number)
        self.logger.debug(f"Content for page {page_number} retrieved.")
        previous_content = expand_response(previous_content, response)
        total_page_number = get_total_page_number(response)
        if (
            total_page_number == page_number or total_page_number == 0
        ):  # Last.FM returns 0 if there is nothing.
            self.logger.debug(
                f"Done handling pagination: {page_number} is the last page."
            )
            return previous_content
        else:
            self.logger.debug("Getting the next page...")
            self.handle_pagination(
                page_number + 1,
                request_next,
                get_total_page_number,
                expand_response,
                previous_content,
            )

    def get_album(
        self, artist: str, album: str, autocorrect: Optional[bool] = None
    ) -> GetAlbumDetailsResponse:
        """Retrieves information for an album.

        :param artist: The name of the album artist.

        :paran album: The name of the album.

        :param autocorrect From the Last.FM API docs:
        Transform misspelled artist names into correct artist names, returning the correct version instead.
        The corrected artist name will be returned in the response."""
        request_parameters = {
            "artist": artist,
            "album": album,
        }
        if autocorrect is None:
            autocorrect = True
        # Translate True or False into 1 or 0.
        request_parameters["autocorrect"]: str = "1" if autocorrect else "0"
        return self.send_request("album.getInfo", request_parameters)

    def get_artist(
        self,
        artist: str,
        autocorrect: Optional[bool] = None,
        language: Optional[str] = None,
    ) -> GetArtistResponse:
        """Retrieves information for an artist.

        :param artist: The aritst name to retrieve.

        :param autocorrect: From the Last.FM API docs:
        Transform misspelled artist names into correct artist names, returning the correct version instead.
        The corrected artist name will be returned in the response.

        :param language: Optional parameter to control biography language.
        """
        request_parameters = {
            "artist": artist,
        }
        if autocorrect is None:
            autocorrect = True
        # Translate True or False into 1 or 0.
        request_parameters["autocorrect"]: str = "1" if autocorrect else "0"
        # Add language if set
        if language is not None:
            request_parameters["language"] = language
        return self.send_request("artist.getInfo", request_parameters)

    def get_tag(self, tag_name: str) -> GetTagInfoResponse:
        """Retrieves information about a tag.

        :param tag_name: The tag name to retrieve."""
        request_parameters = {"tag": tag_name}
        response = self.send_request("tag.getInfo", request_parameters)
        # Detect empty tags
        if response.tag.total == 0 and response.tag.reach == 0:
            raise LastFMDataNotFound("The tag you requested was not found.")
        return response

    def get_scrobbles(
        self,
        user,
        from_time: Optional[datetime.datetime] = None,
        to_time: Optional[datetime.datetime] = None,
        limit: Optional[int] = None,
    ) -> GetRecentTracksResponse:
        """Gets scrobbles for a certain user.

        :param user: The user to retrieve scrobbles for.

        :param from_time: A time interval (start time) to get scrobbles within

        :param to_time A time interval (end time) to get scrobbles within"""
        # Fill out limit and page if not set
        if limit is None:
            limit = 200

        def get_scrobble_page(page_number: int) -> GetRecentTracksResponse:
            """Retrieves the scrobbles on a certain page number.

            :param page_number: The page number"""
            request_parameters = {"user": user, "limit": limit, "page": page_number}
            # The from time and to time should be unix timestamps. Perform the conversion
            if from_time is not None:
                request_parameters["from"]: int = round(from_time.timestamp())
            if to_time is not None:
                request_parameters["to"]: int = round(to_time.timestamp())
            return self.send_request("user.getRecentTracks", request_parameters)

        def get_total_page_number(response: GetRecentTracksResponse) -> int:
            """Gets the total page number of scrobbles."""
            return response.recenttracks.attr.total_pages

        def expand_response(
            previous_content: Optional[GetRecentTracksResponse],
            new_content: Optional[GetRecentTracksResponse],
        ) -> GetRecentTracksResponse:
            """'Adds together' two different responses: one that is has data from the previous page(s)
            and one that is the current response

            :param previous_content: The previous response that contains data from the previous pages.

            :param new_content: A response that contains data from the current page to be added on to previous data."""
            if previous_content is not None:
                previous_content.recenttracks.track.extend(
                    new_content.recenttracks.track
                )
                previous_content.recenttracks.attr = (
                    new_content.recenttracks.attr
                )  # Update the attribute
                return previous_content  # Return the updated content
            else:
                return new_content  # Return the new content on first response

        return self.handle_pagination(
            1, get_scrobble_page, get_total_page_number, expand_response
        )
