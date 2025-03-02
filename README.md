# request-optim

A project to demo optimisation of http get requests. There are two parts of the optimisation process:

1. Deduplication: if a request is made multiple times but one of them is already in flight then they're all returned with the results from the inflight request.

2. Limiting concurrent requests to `N` (default 3): The number of concurrent requests to each endpoint (unique host and port) gets limited and the additional requests are locked until the previous ones have been resolved. The limiting is done via assigning `N` number of semaphores to each endpoint.


Concurrent requests are sent via python `async` methods and the results are handled via `future` (using asyncio).


## env setup

> [!IMPORTANT]
> Ensure that you've `uv` installed: [link](https://docs.astral.sh/uv/getting-started/installation/). 

```bash
uv venv
source .venv/bin/activate
uv sync
```

> [!TIP]
> You can also use the provided devcontainer configuration.
> ```bash
> devcontainer up --workspace-folder .
> ```

## cli

Run the cli using the following command format

```bash
uv run cli.py -n= max number of concurrent requests (default 3) --url=url1 --url=url2 ....
```

Example:

```bash
uv run cli.py --n=3 --url="https://httpbin.org/get" --url="https://httpbin.org/image"
```

Example output:

```bash
2025-03-02 01:53:42.930 | DEBUG    | optimizer.optim:get:73 - Creating semaphore for - httpbin.org:443
2025-03-02 01:53:42.930 | DEBUG    | optimizer.optim:get:83 - Task waiting to acquire semaphore for endpoint: httpbin.org:443
2025-03-02 01:53:42.930 | DEBUG    | optimizer.optim:get:86 - Task acquired semaphore for endpoint: httpbin.org:443
2025-03-02 01:53:42.931 | DEBUG    | optimizer.optim:get:83 - Task waiting to acquire semaphore for endpoint: httpbin.org:443
2025-03-02 01:53:42.932 | DEBUG    | optimizer.optim:get:86 - Task acquired semaphore for endpoint: httpbin.org:443
2025-03-02 01:53:43.381 | DEBUG    | optimizer.optim:get:100 - Task released semaphore for endpoint: httpbin.org:443
2025-03-02 01:53:43.383 | DEBUG    | optimizer.optim:get:100 - Task released semaphore for endpoint: httpbin.org:443
2025-03-02 01:53:43.383 | INFO     | __main__:run:20 - Results:
2025-03-02 01:53:43.384 | INFO     | __main__:run:22 - 
0::
{
  "args": {}, 
  "headers": {
    "Accept": "*/*", 
    "Accept-Encoding": "gzip, deflate", 
    "Host": "httpbin.org", 
    "User-Agent": "Python/3.12 aiohttp/3.11.13", 
    "X-Amzn-Trace-Id": "Root=1-67c3ac17-64847f214e1875477e1ea5e1"
  }, 
  "origin": "*********", 
  "url": "https://httpbin.org/get"
}

2025-03-02 01:53:43.384 | INFO     | __main__:run:22 - 
1::
{"message": "Client did not request a supported media type.", "accept": ["image/webp", "image/svg+xml", "image/jpeg", "image/png", "image/*"]}
2025-03-02 01:53:43.384 | INFO     | __main__:run:23 - Processed 2 requests.
2025-03-02 01:53:43.384 | INFO     | optimizer.optim:__aexit__:110 - Session closed.
```

## demo script

There is a demo script at `src/demo.py` which demoes deduplication.

```bash
uv run demo
```

## testing

```bash
uv run pytest

# or for verbose mode with logging
uv run pytest -svv
```
