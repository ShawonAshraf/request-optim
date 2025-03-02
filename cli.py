import asyncio
from loguru import logger
from optimizer.optim import RequestOptimizer
from typing import List
import argparse

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("--n", type=int, required=True, default=1, help="Max number of concurrent requests.")
argument_parser.add_argument("--urls", action="append", required=True, help="URLs to send requests to.")
args = argument_parser.parse_args()



async def run(n_reqs: int, urls: List[str]):
    optimizer = RequestOptimizer()

    async with optimizer:
        results = await asyncio.gather(*(optimizer.get(url) for url in urls))
        for idx, result in enumerate(results):
            logger.info(f"\n{idx}::\n{result}")
        logger.info(f"Processed {len(results)} requests.")
        
    
if __name__ == "__main__":
    n = args.n
    urls = args.urls
    
    print(args)
    asyncio.run(run(n, urls))
