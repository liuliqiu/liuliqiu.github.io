---
layout: post
title: Python描述器
---

# 描述器协议

Python中的描述器就是满足描述器协议的对象属性。  

```
descr.__get__(self, obj, klass=None) --> value
descr.__set__(self, obj, value) --> None
descr.__delete__(self, obj) --> None
```

只要定义了以上三个接口中的任意一个接口，就满足描述器协议。这实际上就是典型的Python中的鸭子类型。  

```python
class Descriptor(object):
    def __get__(self, obj, klass=None):
        return "x"

class Klass(object):
    field = Descriptor()

obj = Klass()
assert obj.field == "x"
```

其中`__set__`和`__delete__`是相关的，如果只定义了`__set__`没有定义`__delete__`那么删除对象属性时就会抛出`AttributeError`，同样如果只定义了`__delete__`没有定义`__set__`给对象的属性赋值时也会抛出`AttributeError`。  

# 应用

Python中property、instancemethod、staticmethod、classmethod、super背后的机制都是descriptor。  

### property

property就是接收三个函数，返回一个descriptor。  

```
property(fget=None, fset=None, fdel=None, doc=None) -> property attribute
```

[Descriptor Howto Guide中提供了property的纯Python实现](https://docs.python.org/3/howto/descriptor.html#properties)。  

### Function

Python中所有函数对象都有一个`__get__`方法。
实际上 `A().f` 等价于 `A.f.__get__(A())`  
而且对于任意一个函数对象也可以调用`__get__`方法绑定第一个参数的值。

```python
def f(x, y):
    return (x, y)
assert f.__get__(1)(2) == (1, 2)
```

而classmethod和staticmethod都是对函数对象的一种包装。它们等价于下面的Python代码  

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
super(type[, object-or-type]) --> super object
```

Python中super函数实际上返回的是一个代理对象，这样就能构按照原有对象的MRO顺序查找对象的基类属性。但是查找到对象属性之后，super对象会将获取到的属性和原有对象绑定。  

# 历史

描述器是在[Python2.2]中引入到Python中的。Python2.2是一个非常大的版本，引入了非常多的特性。其中最重要的更改就是new-style class、property、staticmethod、classmethod这些基于描述器的特性。  
首先在Python2.2版本之前，Python是按照实例 -> 类 -> 基类的顺序查找对象属性的。但是在查找的属性，如果发现是一个可执行的方法。那么Python会将实例绑定到函数的第一个参数，也就是self上去。这实际上就是原始的描述器`__get__`方法的雏形。  
Python2.2版本中将这一种绑定抽象为`__get__`方法，交给函数去决定怎么绑定实例，是否绑定实例。这样就能引入staticmethod和classmethod了。然后更进一步的就添加上`__set__`和`__delete__`方法。  
当然添加完了`__set__`方法之后原有的属性查找顺序就有问题了。因为原有体系中赋值总是作用于实例的，但是新加上的带有`__set__`方法的描述器必须拦截属性的赋值行为。所以Python就将属性的查找顺序修改成为了data descriptor > 实例属性 > non-data descriptor的查找顺序。  

# 查找顺序

如果一个descriptor只有`__get__`方法，适用"实例-类-基类"的普通查找顺序；如果它同时有`__get__`和`__set__`方法时，适用"类-基类-实例"的特殊查找顺序。  
但是一个descriptor只有查找到之后才能知道是否有`__set__`方法，所以Python在实现中对于所有属性都是按照"类-基类-实例"的属性查找顺序。先查找到描述器，如果是data descriptor就直接返回，否则就去查找实例的属性，没有查找到时返回non-data descriptor。  
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

# 参考资料

- [Descriptor HowTo Guide]
- [PEP 252]
- [What’s New in Python 2.2][Python2.2]
- 知乎《如何理解 Python 的 Descriptor？》问题下刘缙的[答案][descriptor zhihu]
- Python官方文档中datamodel下的[descriptors][python reference datamodel descriptors]部分。
- CPython(3.5)中的[查找属性实现][PyObject_GenericGetAttr]


[Python2.2]: https://docs.python.org/2/whatsnew/2.2.html
[Descriptor HowTo Guide]: https://docs.python.org/3/howto/descriptor.html
[PEP 252]: https://www.python.org/dev/peps/pep-0252/
[prperty]: https://docs.python.org/3/library/functions.html#property
[descriptor zhihu]: https://www.zhihu.com/question/25391709/answer/30634637
[python reference datamodel descriptors]: https://docs.python.org/3/reference/datamodel.html#descriptors
[PyObject_GenericGetAttr]: https://hg.python.org/cpython/file/3.5/Objects/object.c#l1029


