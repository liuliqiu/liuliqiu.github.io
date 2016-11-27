---
layout: post
title: python多任务库 concurrent.futures
---


## 介绍
[concurrent.futures]是在[python 3.2][What's New In Python 3.2]中加入到python标准库中的，不过在python2中也可以[安装使用][pupi futures]。  
[concurrent.futures]提供了管理线程和进程一致的接口  
这个库主要从[java.util.concurrent]包中得到灵感  


### Executor
Executor是一个抽象基类，它提供了一组管理并发的接口。
- `submit(fn, *args, **kwargs)`: 返回一个Future对象。
- `map(fn, *iterables, timeout=None, chunksize=1)`: 提供了python内置的map函数一致的接口。chunksize用于ProcessPoolExcutor一次性提供多个数据给执行进程。
- `shutdown(wait=True)`: 通知正在执行的任务释放资源，wait为False的时候会直接返回，不过Python程序会等到所有任务释放资源后才退出。

futures库实现了Executor的两个子类ThreadPoolExecutor和ProcessPoolExecutor。  
- ThreadPoolExecutor: 因为[GIL]的限制，python中多线程不能完全发挥CPU的性能，所以ThreadPoolExecutor更适合I/O密集型的任务。
- ProcessPoolExecutor: ProcessPoolExecutor使用了多进程，所以摆脱了[GIL]的限制，更适合CPU密集型的任务。但也因此只能使用[pickable][What can be pickled and unpickled]的函数和数据。

### Future
- `cancel()`: 取消当前任务的执行，如果已经执行了或者不能取消时返回False，否则返回True。
- `cancelled()`: 判断是否成功取消。
- `running()`: 判断是否正在运行。
- `done()`: 判断是否成功取消或者执行完毕。
- `result(timeout=None)`: 获取执行结果。
- `exception(timeout=None)`: 获取执行中抛出的异常。
- `add_done_callback(fn)`: 添加回调函数。

### `as_completed(fs, timeout=None)`
接收一个Future序列，按完成顺序返回Future对象。  
### `wait(fs, timeout=None, return_when=ALL_COMPLETED)`
接收一个Future序列，返回一个`(done, not_done)`的`tuple`。  

## [tornado][tornado.concurrent]中的使用
tornado在[tornado.concurrent]中实现了自定义的Future，和标准的Future有少许差别。不过tornado在处理异步程序时可以兼容标准库返回的Future对象。

```python
class AsyncHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            resp = yield executor.submit(requests.get, "http://example.com")
        self.write(resp.text)
```


[What’s New In Python 3.2]: https://docs.python.org/3/whatsnew/3.2.html#pep-3148-the-concurrent-futures-module
[PEP 3148]: https://www.python.org/dev/peps/pep-3148/
[concurrent.futures]: https://docs.python.org/3/library/concurrent.futures.html
[What can be pickled and unpickled]: https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled
[java.util.concurrent]: http://docs.oracle.com/javase/1.5.0/docs/api/java/util/concurrent/package-summary.html
[tornado.concurrent]: http://www.tornadoweb.org/en/stable/concurrent.html
[pypi futures]: https://pypi.python.org/pypi/futures
[github futures]: https://github.com/agronholm/pythonfutures
[GIL]: https://docs.python.org/3/glossary.html#term-global-interpreter-lock

[dalkescientific-concurrent.futures]: http://www.dalkescientific.com/writings/diary/archive/2012/01/19/concurrent.futures.html

