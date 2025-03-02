import aiohttp
import asyncio
from urllib.parse import urlparse
from loguru import logger
import re


class RequestOptimizer:
    def __init__(self):
        # map to store ongoing requests for deduplication: URL -> Future
        self.in_flight_requests = {}
        # map to store endpoint semaphores: "host:port" -> asyncio.Semaphore
        self.endpoint_semaphores = {}
        # a single aiohttp session for all requests.
        self.session = aiohttp.ClientSession()
        # max 3 concurrent requests per endpoint
        self.MAX_CON = 3
        
    def is_url_valid(self, url: str) -> bool:
        URL_REGEX = re.compile(
            r'^(?:http)s?://'            # http:// or https://
            r'(?:\S+(?::\S*)?@)?'
            r'(?:'
            r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3})'  # IP address
            r'|'
            r'(?P<host>[A-Za-z0-9.-]+)'       # domain...
            r')'
            r'(?::\d+)?'                    # optional port
            r'(?:[/?#][^\s]*)?$',            # path, query string, fragment
            re.IGNORECASE
        )
        
        return re.match(URL_REGEX, url) is not None
        

    def get_endpoint(self, url: str) -> str:
        """
        Extracts the endpoint (host and port) from the URL.
        If no port is specified, uses 443 for HTTPS and 80 for HTTP.
        Throws a ValueError if the URL is not valid.
        """
        if self.is_url_valid(url):
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            return f"{host}:{port}"
        else:
            raise ValueError(f"Invalid URL: {url}")


    async def get(self, url: str) -> str:
        """
        Performs an HTTP GET request to the given URL with optimizations:
        - Deduplicates concurrent requests for the same URL.
        - Limits concurrent requests per endpoint to MAX_CON.
        - Uses the entire URL string as the identifier for a request.
        Returns the response body as a string.
        """
        # deduplication: if a request for this URL is already in flight, wait for its result.
        if url in self.in_flight_requests:
            logger.info(f"Request : {url} :: is already in flight!")
            return await self.in_flight_requests[url]

        # a future to represent this request and store it.
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self.in_flight_requests[url] = future

        # determine the endpoint and get/create a semaphore for it.
        try:
            endpoint = self.get_endpoint(url)
            if endpoint not in self.endpoint_semaphores:
                logger.debug(f"Creating semaphore for - {endpoint}")
                self.endpoint_semaphores[endpoint] = asyncio.Semaphore(self.MAX_CON)
            semaphore = self.endpoint_semaphores[endpoint]
        except ValueError as e:
            future.set_exception(e)


        try:
            # if there are more than MAX_CON concurrent requests, it gets locked
            # until MAX_CON requests have been resolved
            logger.debug(
                f"Task waiting to acquire semaphore for endpoint: {endpoint}")
            async with semaphore:
                logger.debug(
                    f"Task acquired semaphore for endpoint: {endpoint}")
                async with self.session.get(url) as response:
                    # return a string for simplicity
                    # ideally there should be handlers based on content type
                    data = await response.text()
                    future.set_result(data)
                    return data
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # once completed, remove the entry for deduplication.
            self.in_flight_requests.pop(url, None)
            logger.debug(f"Task released semaphore for endpoint: {endpoint}")

    
    # https://stackoverflow.com/a/54773296
    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        # close the session at the end
        await self.session.close()
        logger.info("Session closed.")
