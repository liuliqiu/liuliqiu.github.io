---
layout: post
title: Python 类递归
tags:
- Python
---

## 背景

写代码的时候想给类定义一个当前类的实例，像这样

```python
class Test(object):
    instance = Test()
```

但是这样只会报错，因为 `Test` 类当前还没有定义，所以不能实例化，只能像这样写

```python
class Test(object):
    pass
Test.instance = Test()
```

但是这样不优雅，最开始想到的是Y组合子实现的匿名函数递归，但是后面想到了用描述器延迟实例化。

## 实现

使用描述器定义实例，当访问实例时，使用获得的类初始化真正的实例。将实例化延迟到访问类变量时。

```python
class Self(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.instance = None

    def __get__(self, obj, klass=None):
        if klass is not None:
            if self.instance is None:
                self.instance = klass(*self.args, **self.kwargs)
            return self.instance

class Test(object):
    instance = Self()

assert isinstance(Test.instance, Test)
```

