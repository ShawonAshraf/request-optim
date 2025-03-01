import json
from optim import HttpGetOptimizer
import asyncio
from loguru import logger


# Example usage:
async def main():
    optimizer = HttpGetOptimizer()
    
    test_url = "https://httpbin.org/get"
    
    # TODO: add argparse to take the number of requests as cmd args
    # Launch multiple requests concurrently.
    # If duplicate calls are made, they share the same in-flight request.
    results = await asyncio.gather(
        optimizer.get(test_url),
        optimizer.get(test_url),
        optimizer.get(test_url)
    )
    
    results_json = list(map(lambda r: json.loads(r), results))
    logger.info(results_json)
    
    await optimizer.close()

if __name__ == "__main__":
    asyncio.run(main())
