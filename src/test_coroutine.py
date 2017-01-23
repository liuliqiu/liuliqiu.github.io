
import asyncio
import contextlib

async def factorial(name, number):
    result = 1
    for i in range(2, number + 1):
        print("Task {}: Compute factorial({})...".format(name, i))
        await asyncio.sleep(1)
        result *= i
    print("Task {}: factorial({}) = {}".format(name, number, result))
    return result

if __name__ == "__main__":
    with contextlib.closing(asyncio.get_event_loop()) as loop:
        args = [("A", 2), ("B", 3), ("C", 4)]
        tasks = [factorial(name, number) for name, number in args]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        print("All results: {}".format(results))
        for (name, number), result in zip(args, results):
            print("Task {}: factorial({}) = {}".format(name, number, result))


