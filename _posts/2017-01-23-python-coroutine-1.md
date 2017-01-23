---
layout: post
title: Python协程coroutine(1)
tags:
- Python
---


### 协程([coroutine])

什么是协程？协程是一种程序组件，主要是用于解决并发编程问题。对于并发编程可能大家比较熟悉的是使用线程来处理，那为什么还要引入协程呢。那我们首先就要明白线程，了解线程的优缺点。

线程(Thread)是一种系统级并发方案，由系统内核调度，同一个进程间的多个线程共享资源。线程的问题在于线程是抢占式(Preemption)的，由系统控制什么时候获得时间片、什么时候让出时间片。但是线程之间是共享内存的，这就会导致了很多的资源竞争，线程模型引入了各种锁来解决这些资源竞争问题。这种线程与锁模型的缺点在于程序非常难调试，bug很难复现。

协程就是为了解决线程与锁模型的各种问题，而提供的一种更简单、更易于理解的并发编程方式。协程是一种协作式的多任务方案，它是非抢占式(Non-preemption)的。当遇到异步I/O任务时，由协程主动释放CPU资源给事件循环，由事件循环将控制权交给其他协程，等到异步I/O完成时再由事件循环将CPU资源交还给协程。

### 协程的优缺点
协程的优点在于：
1. 代码还是按照之前的的同步程序代码写，但是有效的提高了单线程情况下的CPU利用率。
2. 相比回调来说，协程代码的上下文一致。在多个异步资源的时候不会陷入多层回调函数中。
3. 并发模型相比线程来说更简单，不用考虑复杂的资源共享问题。

协程的缺点在于：
1. 协程实际上还是顺序式的，所以无法像多线程一样充分利用现在的多核资源。但是由于Python本身GIL对于多线程的限制，所以这个缺点对于Python来说并不严重。
2. 协程的实现需要保存上下文以便下次恢复运行状态，相对于回调来说会占用一定的内存资源，但是并不多，支持十万级的协程并发还是很轻松的。
3. 协程是非抢占式的，所以当一个协程不释放控制权的时候其他协程无法执行。


### python中的协程

python通过一系列的慢慢的添加功能，在Python3.5中提供了对于coroutine的完整支持。  
通过[asyncio][PEP 3156]库提供了对于事件循环，异步I/O等的支持。通过[async][PEP 492]定义一个协程，通过[await][PEP 492]释放控制权给事件循环直到协程对象返回结果。  

```python
import asyncio
import contextlib

async def factorial(name, number):          # 定义一个协程
    result = 1
    for i in range(2, number + 1):
        print("Task {}: Compute factorial({})...".format(name, i))
        await asyncio.sleep(1)              # 运行到这时协程会释放掉控制权，将控制权交给事件循环
        result *= i
    print("Task {}: factorial({}) = {}".format(name, number, result))
    return result

with contextlib.closing(asyncio.get_event_loop()) as loop:
    args = [("A", 2), ("B", 3), ("C", 4)]
    tasks = [factorial(name, number) for name, number in args]
    results = loop.run_until_complete(asyncio.gather(*tasks))   # 运行直到所有协程结束
    print("All results: {}".format(results))
    for (name, number), result in zip(args, results):
        print("Task {}: factorial({}) = {}".format(name, number, result))
```

输出：

```
Task A: Compute factorial(2)...
Task C: Compute factorial(2)...
Task B: Compute factorial(2)...
Task A: factorial(2) = 2
Task C: Compute factorial(3)...
Task B: Compute factorial(3)...
Task C: Compute factorial(4)...
Task B: factorial(3) = 6
Task C: factorial(4) = 24
All results: [2, 6, 24]
Task A: factorial(2) = 2
Task B: factorial(3) = 6
Task C: factorial(4) = 24
```

我们可以看到三个任务在交替运行。

## 参考资料

1. [Coroutine Wikipedia][coroutine]
1. [PEP 492]
1. [PEP 3156]

[coroutine]: https://en.wikipedia.org/wiki/Coroutine
[PEP 492]: https://www.python.org/dev/peps/pep-0492/
[PEP 3156]: https://www.python.org/dev/peps/pep-3156/
