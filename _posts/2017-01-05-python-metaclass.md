---
layout: post
title: Python元类metaclass
tags:
- Python
---

## Python面向对象(new-style class)

Python一门面向对象语言，Python中一切都是对象，每个对象都有一个标识，一个类型和一个值<sup>[[1]][Python Data model: Objects, values and types]</sup>。  
而且Python中一切类都是object的子类，也就是说一切对象都是object的实例。  
最后Python中一切类的类都是type的子类，也就是说一切类都是type的实例。  
元类metaclass就是class的class。  

## Python中Class的实现

Python中type函数即可以返回一个对象的类型，也可以用来创建出一个新的类型。

```python
C = type("C", (object, ), {"x": 1})
assert isinstance(C, type)
assert isinstance(C(), C)
assert C.__name__ == "C"
assert C.__bases__ == (object, )
assert C.__dict__["x"] == 1
```

事实上Python在实现的时候，就是把一个自定义类的结构体定义为一个函数，然后直接运行函数获得返回的局部变量字典。使用类名，基类列表和局部变量字典定义一个类。

```python
In [1]: import dis

In [2]: code = compile("""class C(object):x=1""", "<stdin>", "exec")

In [3]: dis.dis(code)
  1         0 LOAD_CONST             0 ('C')                  # 类名
            3 LOAD_NAME              0 (int)
            6 LOAD_NAME              1 (object)
            9 BUILD_TUPLE            2                        # 使用之前压入的两个类型构造基类列表
           12 LOAD_CONST             1 (<code object C at 0x105fc93b0, file "<stdin>", line 1>)
           15 MAKE_FUNCTION          0
           18 CALL_FUNCTION          0                        # 运行函数获得属性字典
           21 BUILD_CLASS                                     # 生成定义的类
           22 STORE_NAME             2 (C)                    # 赋值给变量C
           25 LOAD_CONST             2 (None)
           28 RETURN_VALUE

In [4]: dis.dis(code.co_consts[1])
  1         0 LOAD_NAME              0 (__name__)
            3 STORE_NAME             1 (__module__)
            6 LOAD_CONST             0 (1)
            9 STORE_NAME             2 (x)                    # 定义局部变量x
           12 LOAD_LOCALS                                     # 获取当前函数的局部变量字典
           13 RETURN_VALUE                                    # 返回局部变量字典
```

## metaclass

Python在`BUILD_CLASS`时默认会用type去创建类，不过我们可以通过定义metaclass修改这一行为。  
Python2中通过定义属性`__metaclass__`定义元类，Python3中可以使用新的class定义语法定义元类。Python的兼容性库six定义了函数`with_metaclass`来定义元类。  

```python
class Meta(type):
    pass

class Python2(object):
    __metaclass__ = Meta

class Python3(object, metaclass=Meta):
    pass

from six import with_metaclass
class MyClass(with_metaclass(Meta, object)):
   pass
```

当定义了metaclass时，Python就会去调用`metaclass(name, bases, namespace, **kwds)`去创建一个类。

## 应用



## 参考资料
1. [Python Data model: Objects, values and types]
2. [PEP 3115]
3. [Expert Python Porgramming - Second Edition]

[Python Data model: Objects, values and types]: https://docs.python.org/3/reference/datamodel.html#objects-values-and-types
[PEP 3115]: https://www.python.org/dev/peps/pep-3115/
[Expert Python Porgramming - Second Edition]: https://book.douban.com/subject/26791781/
