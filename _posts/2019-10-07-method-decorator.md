---
layout: post
title: 同时适用于函数和方法的装饰器
tags:
- Python
- decorator
---

## 背景

我们写web框架的view，一般有两种形式，一种是函数形式，另外一种就是类形式的。

```python
def test_view(request, *args, **kwargs):
  # do something
  pass

class TestView:
  def get(self, request, *args, **kwargs):
    # do something
    pass
```

如果我们想要写一个装饰器的时候，就会面对一个问题：函数和方法的签名是不一样的，方法的第一个参数是实例。我们可以通过判断第一个参数的类型，来处理这个问题。不过我们这介绍另一种方法来解决这个问题。

## 实现

我们利用描述器来解决这个问题，python获取一个属性时，会调用属性的 `__get__` 方法将属性和实例绑定。

```python
class Wrap(object):
  def __init__(self, func):
    self.func = func
    self.__doc__ = func.__doc__
  def __call__(self, request, *args, **kwargs):
    print(request, args, kwargs)
    return self.func(request, *args, **kwargs)
  def __get__(self, obj, klass=None):
    self.func = self.func.__get__(obj, klass)
    return self
```

试一下

```python
@Wrap
def test_view(request, *args, **kwargs):
  # do something
  pass

class TestView:
  @Wrap
  def get(self, request, *args, **kwargs):
    # do something
    pass
test_view("request_function")   # request_function () {}
TestView().get("request_method") # request_method () {}
```

嗯，逻辑没问题，但是不通用，每一个装饰器都写这么一大段代码，麻烦。所以我们更进一步，写一个装饰器的装饰器，任何使用了这个装饰器的装饰器都既可以用于函数也可以用于方法。

```python
def general_wrap(wrap):
  class wrapper:
    def __init__(self, func):
      self.func = func
      self.__doc__ = func.__doc__
    def __call__(self, *args, **kwargs):
      return wrap(self.func)(*args, **kwargs)
    def __get__(self, obj, klass=None):
      return wrapper(self.func.__get__(obj, klass))
  return wrapper

@general_wrap
def show_args(func):
  def wrapper(request, *args, **kwargs):
    print(request, args, kwargs)
    return func(request, *args, **kwargs)
  return wrapper

@show_args
def test_view(request, *args, **kwargs):
  pass

class TestView:
  @show_args
  def get(self, request, *args, **kwargs):
    pass

test_view("request_function")     # request_function () {}
TestView().get("request_method")  # request_method () {}
        
```

搞定。

