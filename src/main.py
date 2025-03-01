import asyncio

from loguru import logger

from optimizer.optim import RequestOptimizer


# Example usage:
async def run_optimizer():
    optimizer = RequestOptimizer()
    N_REQS = 5

    urls = ["https://httpbin.org/get"] * N_REQS + \
        ["https://httpbin.org/status/404"] * N_REQS + \
        ["https://httpbin.org/ip"] * N_REQS + \
        ["https://httpbin.org/image"] * N_REQS

    async with optimizer:
        results = await asyncio.gather(*(optimizer.get(url) for url in urls))
        logger.info(f"Processed {len(results)} requests.")


def main():
    asyncio.run(run_optimizer())


if __name__ == "__main__":
    main()
