---
layout: post
title: python多任务库 concurrent.futures
---

## 介绍
[concurrent.futures]是在[python 3.2]中加入到python标准库中的，不过在python2中也可以[安装使用][pypi futures]。这个库来源于[java.util.concurrent]。提供了管理线程和进程多任务一致的接口。  

### Executor
Executor是一个抽象基类，它提供了一组管理并发的接口。
- `submit(fn, *args, **kwargs)`: 返回一个Future对象。
- `map(fn, *iterables, timeout=None, chunksize=1)`: 提供了python内置的map函数一致的接口。chunksize用于ProcessPoolExcutor一次性提供多个数据给执行进程。
- `shutdown(wait=True)`: 通知正在执行的任务释放资源，wait为False的时候会直接返回，不过Python程序会等到所有任务释放资源后才退出。

futures库实现了Executor的两个子类。  
- ThreadPoolExecutor: 因为[GIL]的限制，python中多线程不能完全发挥CPU的性能，所以更适合I/O密集型的任务。
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

```python
import concurrent.futures
import urllib.request

URLS = ['http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://some-made-up-domain.com/']

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()

# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))
```

## 死锁
并发的时候肯定要考虑死锁的问题，不过使用Executor时要特别注意Excutor对象本身的资源占用也有可能会造成死锁。比如官方的例子:  
```python
def wait_on_future():
    f = executor.submit(pow, 5, 2)
    # This will never complete because there is only one worker thread and
    # it is executing this function.
    print(f.result())

executor = ThreadPoolExecutor(max_workers=1)
executor.submit(wait_on_future)
```

## [tornado][tornado.concurrent]中的使用
tornado在[tornado.concurrent]中实现了自定义的Future，和标准的Future有少许差别。不过tornado可以兼容使用标准库的Future对象。

```python
class AsyncHandler(web.RequestHandler):
    @gen.coroutine
    def get(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            resp = yield executor.submit(requests.get, "http://example.com")
        self.write(resp.text)
```

参考资料:
1. [What's New In Python 3.2][python 3.2]
2. [PEP 3148]
3. [concurrent.futures]
4. [tornado.concurrent]

[python 3.2]: https://docs.python.org/3/whatsnew/3.2.html#pep-3148-the-concurrent-futures-module "What’s New In Python 3.2"
[PEP 3148]: https://www.python.org/dev/peps/pep-3148/ "PEP 3148"
[concurrent.futures]: https://docs.python.org/3/library/concurrent.futures.html
[pypi futures]: https://pypi.python.org/pypi/futures
[github futures]: https://github.com/agronholm/pythonfutures
[What can be pickled and unpickled]: https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled
[java.util.concurrent]: http://docs.oracle.com/javase/1.5.0/docs/api/java/util/concurrent/package-summary.html
[tornado.concurrent]: http://www.tornadoweb.org/en/stable/concurrent.html
[GIL]: https://docs.python.org/3/glossary.html#term-global-interpreter-lock
[dalkescientific-concurrent.futures]: http://www.dalkescientific.com/writings/diary/archive/2012/01/19/concurrent.futures.html

