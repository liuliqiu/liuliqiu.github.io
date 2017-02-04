---
layout: post
title: Python协程coroutine(2)
tags:
- Python
- coroutine
- concurrency
---

Python 中的协程是建立在生成器(generator)上的，我们从生成器开始来了解 Python 中协程的实现。

# 生成器

[Python2.3] 中加入了[简单的生成器][PEP255]，但是这时候的生成器还是非常简单的，只是通过函数实现迭代器功能。

## Python 中的的函数运行机制

要了解 generator 的实现，就必须先了解 Python 中函数的实现和运行机制<sup>[[1]][Python源码剖析]</sup>。

在 Python 中一切都是对象，每一个函数实际上都是一个 function 对象。当函数运行时 Python 会将 function 对象和运行的上下文放在一起包装成一个 frame 对象。frame 的意思是栈帧，每个 frame 对象都有一个 f_back 指针指向调用者的 frame 对象。运行时函数之间的调用就会形成一个 frame 的链表，这个链表就是 Python 中的栈。

我们要注意到 Python 的函数运行机制有两点需要特别注意。第一点 Python 中的栈是栈帧组成的链表，不是连续的内存空间。第二点 Python 中所有运行状态都是保存在栈帧中，没有使用寄存器保存运行状态。

## generator 的实现

首先，所有 generator 函数的 function 对象都会有一个标志位指明这个函数是生成器函数。这样在执行时就可以通过标志位和普通函数区别开来。generator 函数执行时会和普通函数一样构造一个 frame 对象，但是和普通函数不一样的地方在于它不会执行这个 frame 对象，而是会先将这个对象的 f_back 指针清除，然后使用这个 frame 对象实例化一个 generator 对象，然后直接返回 generator 对象。

generator 对象实现了迭代器协议，调用它的 `__next__` 方法会运行保存的栈帧，运行中遇到栈帧中的 yield 时会将得到的值返回。

yield 和普通函数中 return 的区别在于：return 会清理 frame 释放内存，而 yield 会跳过清理 frame 的代码，这样下次才能继续运行函数。

{% highlight python linenos %}
def f():
    yield 1
    for i in [2, 3]:
        yield i * i

gen = f()
frame = gen.gi_frame
for v in gen:
    print("val: {}, lineno:{}, locals:{}".format(v, frame.f_lineno, frame.f_locals))
    # gi_frame 就是函数的栈帧，f_lineno 表示当前栈帧执行到的行数，f_locals是局域变量。
{% endhighlight %}
输出为：
```python
val: 1, lineno:2, locals:{}
val: 4, lineno:4, locals:{'i': 2}
val: 9, lineno:4, locals:{'i': 3}
```

# 生成器的加强

[Python2.5] 中生成器功能得到了[加强][PEP342]，开始允许通过send向生成器传递数据，并且允许通过 throw 和 close 方法向生成器抛出异常。实现了迭代器与外部之间的交互。

{% highlight python linenos %}
class Error(Exception): pass
def f():
    x = 1
    x = yield x
    try:
        x = yield x
    except Error:
        print("generator error: Error")
        x = yield x + 1
    try:
        yield x
    except GeneratorExit:
        print("generator error: GeneratorExit")
        # generator 遇到 GeneraotrExit 时必须退出，否则 close 方法会抛出 RuntimeError。

gen = f()
# 第一次调用生成器必须用next，或者send(None)
assert gen.send(None) == 1
assert gen.gi_frame.f_lineno == 4

assert gen.send(12) == 12
assert gen.gi_frame.f_lineno == 6

assert gen.throw(Error) == 13   # generator error: Error
assert gen.gi_frame.f_lineno == 9

assert next(gen) is None
assert gen.gi_frame.f_lineno == 11

assert gen.close() == None      # generator error: GeneratorExit
assert gen.gi_frame is None

{% endhighlight %}

# yield from
[Python3.3] 中新加入 [yield from][PEP380]，可以直接将迭代委托给一个迭代器，并且处理了异常和数据传递。同时允许了迭代器中使用return抛出StopIteration。

{% highlight python linenos %}
def f():
    x = yield 1
    yield x

def g():
    yield from f()
    x = yield 3
    return x

gen = g()

assert next(gen) == 1
assert gen.gi_frame.f_lineno == 6
assert gen.gi_yieldfrom.gi_frame.f_lineno == 2

assert gen.send(2) == 2
assert gen.gi_frame.f_lineno == 6
assert gen.gi_yieldfrom.gi_frame.f_lineno == 3

assert next(gen) == 3
assert gen.gi_frame.f_lineno == 7
assert gen.gi_yieldfrom is None

try:
    gen.send(4)
except StopIteration as e:
    assert e.value == 4
{% endhighlight %}


## 参考资料

1. [Python源码剖析] 8.1 Python虚拟机中的执行环境
1. [PEP255]
1. [PEP342]
1. [PEP380]
1. [PEP3156]
1. [PEP492]


[PEP255]: https://www.python.org/dev/peps/pep-0255/
[PEP342]: https://www.python.org/dev/peps/pep-0342/
[PEP288]: https://www.python.org/dev/peps/pep-0288/
[PEP325]: https://www.python.org/dev/peps/pep-0325/
[PEP380]: https://www.python.org/dev/peps/pep-0380/
[PEP3156]: https://www.python.org/dev/peps/pep-3156/
[PEP492]: https://www.python.org/dev/peps/pep-0492/
[PEP255]: https://www.python.org/dev/peps/pep-0255/
[Python2.3]: https://docs.python.org/3/whatsnew/2.3.html#pep-255-simple-generators
[Python2.5]: https://docs.python.org/3/whatsnew/2.5.html#pep-342-new-generator-features
[Python3.3]: https://docs.python.org/3/whatsnew/3.3.html#pep-380-syntax-for-delegating-to-a-subgenerator
[Python3.4]: https://docs.python.org/3/whatsnew/3.4.html#asyncio
[Python3.5]: https://docs.python.org/3/whatsnew/3.5.html#pep-492-coroutines-with-async-and-await-syntax
[Python源码剖析]: https://book.douban.com/subject/3117898/

