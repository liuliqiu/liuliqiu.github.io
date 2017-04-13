什么是协程？可能大家都比较熟悉进程和线程，那么协程又是什么鬼，为什么有了进程线程还不够还要有协程？  
进程的目的是隔离不同的程序运行，所以不同进程之间的内存空间是隔离的。  

Generators - semicoroutines  
Communicating sequential processes  
continuation    保存当前上下文  

[并发之痛Thread,Goroutine,Actor]: http://jolestar.com/parallel-programming-model-thread-goroutine-actor/

## python内置协程实现
### [Python3.4] 中加入了异步I/O库 [asyncio][PEP3156]。
并发编程中一个重要的问题就是I/O的阻塞。因为所有的协程本质上还是一个线程上的操作，如果I/O操作阻塞线程的话，所有协程都会被阻塞。所以在Python3.4中加入了标准库 asyncio。
aysncio的核心是EventLopp，标准库中提供了SelectorEventLoop和ProactorEventLoop两种消息循环实现。
SelectorEventLoop基于Reactor模式的异步I/O多路复用(kqueue/epoll/poll/select)。Python3.4中同时在标准库中加入了selectors，这是一个基于select库实现的更高层次的I/O多路复用抽象。
ProactorEventLoop基于Proactor模式的[IOCP(Input/Output Completion Port)]，只能在Windows下使用。


### [Python3.5] 中引入新关键词 [async/await][PEP492] 用于异步编程，并且区分了生成器对象和协程对象。

[Comparing Two High-Performance I/O Design Patterns]: http://www.artima.com/articles/io_design_patterns.html
[I/O Completion Ports]: https://msdn.microsoft.com/en-us/library/windows/desktop/ms740141%28v=vs.85%29.aspx

