---
layout: post
title: python描述器
---

python中的描述器就是满足描述器协议的对象属性。这就是python 中的鸭子类型、看起来是个鸭子的就是鸭子。
描述器是在python2.2中引入到python中的。old-style class转为new-style class时。

# 描述器协议

```
descr.__get__(self, obj, type=None) --> value
descr.__set__(self, obj, value) --> None
descr.__delete__(self, obj) --> None
```
只要定义了以上三个接口中的任意一个接口，就满足描述器协议。
其中`__set__`和`__delete__`是相互依存的，如果只定义了`__set__`没有定义`__delete__`那么删除时就会抛出`AttributeError`，同样如果只定义了`__delete__`没有定义`__set__`赋值时也会抛出`AttributeError`。  

# 查找顺序
如果一个descriptor只有`__get__`方法(如FunctionType)，我们就认为它是function-like descriptor，适用"实例-类-基类"的普通查找顺序；  
如果它有`__set__`方法(如Property)，就是data-like descriptor，适用"类-基类-实例"的特殊查找顺序。  
但是一个descriptor只有查找到之后才能直到是否有`__set__`方法，所以Python在实现中对于所有属性都是按照"类-基类-实例"的属性查找顺序。  
所以实际上Python中，找到一个实例属性，比找到类属性更慢。  

```python
from __future__ import print_function

class FunctionDescriptor(object):
    def __get__(self, obj, type=None):
        print(self.__class__.__name__, "__get__")
        return "get"

class DataDescriptor(object):
    def __get__(self, obj, type=None):
        print(self.__class__.__name__, "__get__")
        return "get"
    def __set__(self, obj, value):
        print(self.__class__.__name__, "__set__")
    def __delete__(self, obj):
        print(self.__class__.__name__, "__delete__")

class Class(object):
    pass

obj = Class()
Class.x = FunctionDescriptor()  # 然后定义类的属性为FunctionDescriptor
obj.x = 1                       # 然后给实例的属性赋值时会将属性赋值到实例上
assert obj.x == 1               # 这时会优先使用实例的属性
del obj.x                       # 删除时会删除实例的属性
assert obj.x == "get"     # FunctionDescriptor __get__

obj.x = 1
Class.x = DataDescriptor()
assert obj.x == "get"    # DataDescriptor __get__
obj.x = 2                # DataDescriptor __set__
assert obj.x == "get"    # DataDescriptor __get__
del obj.x                # DataDescriptor __delete__
assert obj.x == "get"    # DataDescriptor __get__
assert obj.__dict__["x"] == 1
# 同时定义了DataDescriptor和实例属性时会优先使用DataDescriptor
# 不过实例的属性一直都在__dict__中
```

# 应用
Python中property、instancemethod、staticmethod、classmethod、super背后的机制都是descriptor。  

