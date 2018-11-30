---
layout: post
title: Python协程coroutine(3)
tags:
- Python
- coroutine
- concurrency
---

# Python 中的其他协程实现

之前说的都是 Python 中内置的协程实现，但是实际上 Python 中还有其他不同的协程实现。

### stackless
[Stackless Python] 是基于 CPython 的一种 Python 实现，但是它解耦了 Python 函数调用和 C 函数调用的对应关系。CPython 中通过函数 `PyEval_EvalFrame` 的递归调用来实现函数调用，而 Stackless Python 则将通过循环来实现函数调用。这样就能实现 Python 执行状态的保存和恢复。

Stackless Python 提供了一种微线程(microthread)叫做 `tasklet` 以及微线程之间通讯的 `channel`。`tasklet` 和 `channel` 都是第一类对象，可以序列化保存然后反序列化出来，这样就可以实现程序状态的存储。微线程实际上就是协程，都是非抢占式多任务处理，只是同一种东西的不同称呼。

CSP(communicating sequential processes)模型是一种重要的异步编程模式。在 CSP 模型多个异步任务之间通过 `channel` 进行通信。`channel` 有两个方法 `send` 和 `receive`，当协程中调用 `send` 发送消息时，协程会阻塞直到消息被别的协程 `receive`。而当协程中调用 `receive` 接受消息但是 `channel` 中没有消息时，协程也会阻塞直到有协程 `send` 消息。

```python
import stackless

def producer(ch):
    for i in range(3):
        print "send", i
        ch.send(i)

def consumer(ch):
    while True:
        i = ch.receive()
        print "receive", i

ch = stackless.channel()
stackless.tasklet(consumer)(ch)
stackless.tasklet(producer)(ch)
stackless.run()
```
执行后输出
```
send 0
receive 0
send 1
receive 1
send 2
receive 2
```


### greenlet

[greenlet] 是 Stackless Python 的副产品。因为 Stackless Python [并没有被CPython接受][PEP219]。所以 greenlet 作为 CPython 的一个 C 拓展，提供了微线程 `greenlet`。

greenlet 是不支持序列化的，所以它只是协程但并不是延续性。

### PyPy

PyPy是Python的一个JIT实现，目标是改进Python的性能。它吸收了Stackless的特性提供了_continuation库，并且基于这个库实现了 `stackless` 和 `greenlet` 两个兼容库。文章中的所有代码都是在 PyPy 5.7.0(python 2.7.13)下测试通过。


# 程序控制流

控制流就是程序执行的顺序。最简单的顺序、条件、循环、子程序等控制流是是编程的基础，

### 顺序、条件、循环

命令式编程范式中，程序指令按照顺序一条一条执行，并且可以通过条件分支语句选择执行或者不执行某些指令，也可以通过循环语句重复执行部分指令。这些都是基本的程序控制流。 而协程和延续性则实现了多个程序控制流之间切换，但是这几个程序控制流和切换一起总体上来看实际上是一个控制流。

### 子程序(subroutine)

运行另一段指令，然后返回原指令中断继续执行。也就是函数和面向对象中的方法。

### 对称协程(symmetric coroutines)又被称为半协程(semi-coroutines)

对称协程指的是控制流只能在调用函数和协程之间切换。所有基于 generator 实现的协程(包括 Python 中内置的协程)都是对称协程。

子程序可以算作对称协程的一种特例，将控制权交给子程序执行完成后直接返回值。而对称协程只是暂时返回，下次调用还可以继续接下来的指令流。子程序可以看作如果对称协程只返回一次之后没有后面的指令流。

### 不对称协程(asymmetric coroutines)

不对称协程则可以在协程之间任意切换控制流，甚至可以递归切换控制流。Stackless Python 和 greenlet 实现的微线程都是不对称协程。

不对称协程功能性更强，所以对称协程也被称为半协程，半协程可以用协程进行模拟，这是一个用greenlet实现的例子。

```python
import greenlet

def generator(n):
    assert (yield 0) == 123
    yield n

def test_generator():
    coroutine = generator(3)
    assert coroutine.next() == 0
    assert coroutine.send(123) == 3

def coroutine(n):
    assert greenlet.getcurrent().parent.switch(0) == 123
    greenlet.getcurrent().parent.switch(n)

def test_coroutine():
    gr = greenlet.greenlet(coroutine)
    assert gr.switch(3) == 0
    assert gr.switch(123) == 3
```

### 延续性(cotinuation):

延续性指的是程序控制流的运行状态。通常延续性指的是延续性为第一类对象，也就是程序可以在任意时间点存储目前的运行状态，并且在之后回到之前存储的运行状态。延续性只在少数语言中实现，其中最出名的就是scheme中的call/cc函数，所以有时会用call/cc指代延续性。

```python
import _continuation
import pickle

def copy(data):
    return pickle.loads(pickle.dumps(data))

def f(cont):
    print "begin"
    cont.switch()
    print "end"

task = _continuation.continulet(f)
task.switch()
task2 = copy(task)
task.switch()
task2.switch()
```
执行后输出
```
begin
end
end
```


[Stackless Python]: https://bitbucket.org/stackless-dev/stackless/wiki/Home
[what is Stackless]: https://cosmicpercolator.com/2016/02/02/what-is-stackless/
[Stackless Python并发式编程介绍]: https://gashero.yeax.com/?p=30
[why stackless]: https://github.com/grant-olson/why_stackless
[greenlet]: https://greenlet.readthedocs.io/en/latest/
[PEP219]: https://www.python.org/dev/peps/pep-0219/
