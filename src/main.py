from optimizer.optim import HttpGetOptimizer
import asyncio
from loguru import logger


# Example usage:
async def run_optimizer():
    optimizer = HttpGetOptimizer()

    url_root = "https://httpbin.org/get"
    # create 50 requests
    test_urls = [url_root + f"?{i}" for i in range(50)]

    # TODO: add argparse to take the number of requests as cmd args
    # TODO: add different endpoints
    # TODO: yes also add unit tests

    async with optimizer:
        results = await asyncio.gather(*(optimizer.get(tu) for tu in test_urls))
        logger.info(f"Processed {len(results)} requests.")


def main():
    asyncio.run(run_optimizer())


if __name__ == "__main__":
    main()
