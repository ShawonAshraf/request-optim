import aiohttp
import asyncio
from urllib.parse import urlparse
from loguru import logger


class HttpGetOptimizer:
    def __init__(self):
        # Map to store ongoing requests for deduplication: URL -> Future
        self.in_flight_requests = {}
        # Map to store endpoint semaphores: "host:port" -> asyncio.Semaphore
        self.endpoint_semaphores = {}
        # Create a single aiohttp session for all requests.
        self.session = aiohttp.ClientSession()

    def get_endpoint(self, url: str) -> str:
        """
        Extracts the endpoint (host and port) from the URL.
        If no port is specified, uses 443 for HTTPS and 80 for HTTP.
        """
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        return f"{host}:{port}"

    async def get(self, url: str) -> str:
        """
        Performs an HTTP GET request to the given URL with optimizations:
        - Deduplicates concurrent requests for the same URL.
        - Limits concurrent requests per endpoint to 3.
        - Uses the entire URL string as the identifier for a request.
        Returns the response body as a string.
        """
        # Deduplication: if a request for this URL is already in flight, wait for its result.
        if url in self.in_flight_requests:
            logger.info(f"Request : {url} :: is already in flight!")
            return await self.in_flight_requests[url]

        # Create a future to represent this request and store it.
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self.in_flight_requests[url] = future

        # Determine the endpoint and get/create a semaphore for it.
        endpoint = self.get_endpoint(url)
        if endpoint not in self.endpoint_semaphores:
            logger.info(f"Creating semaphore for - {endpoint}")
            self.endpoint_semaphores[endpoint] = asyncio.Semaphore(3)
        semaphore = self.endpoint_semaphores[endpoint]

        try:
            # if there are more than 3 concurrent requests, it gets locked
            # until 3 requests have been resolved
            logger.info(
                f"Task waiting to acquire semaphore for endpoint: {endpoint}")
            async with semaphore:
                logger.info(
                    f"Task acquired semaphore for endpoint: {endpoint}")
                async with self.session.get(url) as response:
                    # Assuming text response
                    data = await response.text()
                    future.set_result(data)
                    return data
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # Once complete (whether successful or not), remove the entry for deduplication.
            self.in_flight_requests.pop(url, None)
            logger.info(f"Task released semaphore for endpoint: {endpoint}")


    async def close(self):
        """Closes the aiohttp session."""
        await self.session.close()
