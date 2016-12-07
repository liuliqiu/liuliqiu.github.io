---
layout: post
title: python描述器
---


# 描述器协议
python中的描述器就是满足描述器协议的对象属性。  
```
descr.__get__(self, obj, klass=None) --> value
descr.__set__(self, obj, value) --> None
descr.__delete__(self, obj) --> None
```
只要定义了以上三个接口中的任意一个接口，就满足描述器协议。  
这实际上就是典型的python中的鸭子类型：看起来是个鸭子的就是鸭子。  
```python
class Descriptor(object):
    def __get__(self, obj, klass=None):
        return "x"

class Klass(object):
    field = Descriptor()

obj = Klass()
assert obj.field == "x"
```
其中`__set__`和`__delete__`是相互依存的，如果只定义了`__set__`没有定义`__delete__`那么删除对象属性时就会抛出`AttributeError`，同样如果只定义了`__delete__`没有定义`__set__`给对象的属性赋值时也会抛出`AttributeError`。  

# 应用
Python中property、instancemethod、staticmethod、classmethod、super背后的机制都是descriptor。  

### property
property很明显就是接收三个函数，返回一个descriptor。  
```
property(fget=None, fset=None, fdel=None, doc=None) -> property attribute
```
Descriptor Howto Guide中提供了property的[纯python实现](https://docs.python.org/3/howto/descriptor.html#properties)。  

### Function
python中所有函数对象都有一个`__get__`方法。
实际上 `A().f` 等价于 `A.f.__get__(A())`  
而且对于任意一个函数对象也可以调用`__get__`方法绑定第一个参数的值。
```python
def f(x, y):
    return (x, y)
assert f.__get__(1)(2) == (1, 2)
```

而实际上classmethod和staticmethod都是对函数对象的一种包装。等价于下面的python代码  
```python
class StaticMethod(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, klass=None):
        return self.f

class ClassMethod(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        def newfunc(*args, **kwargs):
            return self.f(klass, *args, **kwargs)
        return newfunc
```

### super
```
super(type[, object-or-type])
```
python中super函数实际上返回的是一个代理对象，查找代理对象的属性的时候实际上会按第一个参数的MRO查找属性。  


# 历史
描述器是在python2.2中引入到python中的。old-style class转为new-style class时。

# 查找顺序
如果一个descriptor只有`__get__`方法(如FunctionType)，我们就认为它是function-like descriptor，适用"实例-类-基类"的普通查找顺序；  
如果它有`__set__`方法(如Property)，就是data-like descriptor，适用"类-基类-实例"的特殊查找顺序。  
但是一个descriptor只有查找到之后才能知道是否有`__set__`方法，所以Python在实现中对于所有属性都是按照"类-基类-实例"的属性查找顺序。  
所以实际上Python中，找到一个实例属性，比找到类属性更慢。  

```python
from __future__ import print_function

class FunctionDescriptor(object):
    def __get__(self, obj, klass=None):
        print(self.__class__.__name__, "__get__")
        return "get"

class DataDescriptor(object):
    def __get__(self, obj, klass=None):
        print(self.__class__.__name__, "__get__")
        return "get"
    def __set__(self, obj, value):
        print(self.__class__.__name__, "__set__")
    def __delete__(self, obj):
        print(self.__class__.__name__, "__delete__")

class Klass(object):
    pass

obj = Klass()
Klass.x = FunctionDescriptor()  # 然后定义类的属性为FunctionDescriptor
obj.x = 1                       # 然后给实例的属性赋值时会将属性赋值到实例上
assert obj.x == 1               # 这时会优先使用实例的属性
del obj.x                       # 删除时会删除实例的属性
assert obj.x == "get"     # FunctionDescriptor __get__

obj.x = 1
Klass.x = DataDescriptor()
assert obj.x == "get"    # DataDescriptor __get__
obj.x = 2                # DataDescriptor __set__
assert obj.x == "get"    # DataDescriptor __get__
del obj.x                # DataDescriptor __delete__
assert obj.x == "get"    # DataDescriptor __get__
assert obj.__dict__["x"] == 1
# 同时定义了DataDescriptor和实例属性时会优先使用DataDescriptor
# 不过实例的属性一直都在__dict__中
```


[Descriptor HowTo Guide]: https://docs.python.org/3/howto/descriptor.html
[PEP 252]: https://www.python.org/dev/peps/pep-0252/
[prperty]: https://docs.python.org/3/library/functions.html#property

