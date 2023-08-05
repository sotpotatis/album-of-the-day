import io
import time

import requests
from pathlib import Path
from typing import Optional

# Names for OCR languages
class Languages:
    SWEDISH = "swe"
    ENGLISH = "eng"


# Different OCR languages. Description taken from the OCR
# API docs
class OCREngines:
    OCR_ENGINE_1 = "1" # Old, fast
    OCR_ENGINE_2 = "2" # New, powerful
    OCR_ENGINE_3 = "3" # Beta, experimental, recognizes Thai characters


# OCR API exception
class OCRAPIException(Exception):
    pass


# OCR API client
class OCRAPIClient:
    def __init__(self, api_key:str, base_url:Optional[str]=None):
        self.api_key = api_key
        if base_url is None:
            base_url = "https://api.ocr.space"
        self.base_url = base_url.strip("/")

    def authenticated_request(self, method, api_path, headers=None, data=None, files=None, other_kwargs=None):
        if headers is None:
            headers = {}
        headers["apiKey"] = self.api_key
        if other_kwargs is None:
            other_kwargs = {}
        # Add all keyword arguments to the kwargs to pass.
        request_kwargs = other_kwargs
        request_kwargs["url"] = self.base_url + api_path
        request_kwargs["method"] = method
        request_kwargs["headers"] = headers
        request_kwargs["data"] = data
        request_kwargs["files"] = files
        # Create and send request
        response = requests.request(**request_kwargs)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                response_content = response.content.decode()
                raise OCRAPIException(f"Failed converting JSON of response from OCR server. Response content: {response_content}")
        else:
            response_content = response.content.decode()
            raise OCRAPIException(f"Got unexpected status code {response.status_code} and response {response_content} from server.")

    def get_text(self, file_path, language:str, ocr_engine:str):
        """Sends a request to the OCR API.

        :param file_path: The file path (open(file, "r").read())"""
        # Get name of input file
        input_file_path = Path(file_path)
        input_file_name = f"{input_file_path.name}.{input_file_path.suffix}"
        input_file_content = open(file_path, "rb").read()
        api_response = self.authenticated_request("POST", "/parse/image", headers={
            "language": language,
            "OCREngine": ocr_engine
        },
       files={
           input_file_name: input_file_content
       })
        return api_response

