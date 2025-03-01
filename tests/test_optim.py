import pytest
import pytest_asyncio
from optimizer.optim import HttpGetOptimizer
import asyncio


@pytest_asyncio.fixture
async def optimizer():
    return HttpGetOptimizer()


def test_get_endpoint(optimizer):
    url_https = "https://https.xyz"    
    url_http = "http://http.xyz"
    url = "http://url.xyz:8080"
    
    assert optimizer.get_endpoint(url_https) == "https.xyz:443"    
    assert optimizer.get_endpoint(url_http) == "http.xyz:80"    
    assert optimizer.get_endpoint(url) == "url.xyz:8080"


@pytest.mark.asyncio
async def test_get(optimizer):
    # ideally the request calling will be mocked
    # but keeping this simple here
    # also need to test the semaphores
    url_root = "https://httpbin.org/get"
    # create 15 requests
    N_REQS = 15
    test_urls = [url_root + f"?{i}" for i in range(N_REQS)]
    
    
    async with optimizer:
        results = await asyncio.gather(*(optimizer.get(tu) for tu in test_urls))
        assert len(results) == 15, f"There should be exactly {N_REQS} results."
        
@pytest.mark.asyncio
async def test_session_closing(optimizer):
    async with optimizer:
        pass
    
    assert optimizer.session.closed, "The session must be closed after exiting the context"
