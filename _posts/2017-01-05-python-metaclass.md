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
元类metaclass指的就是class的class。  

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
# python 2.7中执行，其他版本可能略有差异。
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
使用metaclass的主要目的在于通过拦截类的创建来修改类。

## 应用
ORM的通常会用metaclass实现，ORM会把数据库中的表映射为对象。使用metaclass就可以通过定义类来描述表的结构，然后通过metaclass中的钩子代码将所有表信息收集。  
因为在类中定义表中每个字段在数据库中的存储形式，在使用实例的时候又需要使用从数据库中获取到的值，所以在实现的时候都会将类定义的Field经过一层描述器的包装。  
下面是一个简化之后的peewee的Model代码。  

```python
class FieldDescriptor(object):          # 包装Field的描述器
    def __init__(self, field):
        self.field = field
        self.att_name = self.field.name

    def __get__(self, instance, instance_type = None):
        if instance is not None:
            return instance._data.get(self.att_name)
        return self.field

    def __set__(self, instance, value):
        instance._data[self.att_name] = value


class Field(object):                    # Field类，通常会根据数据库中的类型定义Field的各种子类
    def add_to_class(self, model_class, name):
        self.name = name
        model_class._fields.append(self)
        setattr(model_class, name, FieldDescriptor(self))


class BaseModel(type):                  # Model的元类
    inheritable = set([])

    def __new__(cls, name, bases, attrs):
        cls = super(BaseModel, cls).__new__(cls, name, bases, attrs)
        if name == "Model":
            return cls                  # 只在定义Model的子类时，才会是定义ORM模型

        cls._fields = []
        cls._data = None
        cls._name = name.lower()        # 定义表名，一般根据模型名生成，或者在Meta中定义
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                attr.add_to_class(cls, name)        # 将Field定义修改为描述器
        return cls


class Model(object):
    __metaclass__ = BaseModel
    def __init__(self, *args, **kwargs):
        self._data = {}             # 在self._data中保存字段数据
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def select(cls):
        fields= ", ".join(field.name for field in cls._fields)
        sql = "SELECT ({fields}) FROM {table_name}".format(table_name=cls._name, fields=fields)
        for data in cls.Meta.db.execute(sql):
            yield cls(**{field.name:value for field, value in zip(cls._fields, data)})

if __name__ == "__main__":
    import sqlite3
    class User(Model):
        name = Field()
        class Meta(object):
            db = sqlite3.Connection("user.db")

    for user in User.select():
        print(user.name)
```



## 参考资料
1. [Python Data model: Objects, values and types]
2. [Python Data model: metaclasses]
3. [PEP 3115]
4. [Expert Python Porgramming - Second Edition]
5. [what is a metaclass in python] 中文版:[深入理解Python中的元类(metaclass)]，[什么是metaclass]
6. [peewee 2.8.5 Model]

[Python Data model: Objects, values and types]: https://docs.python.org/3/reference/datamodel.html#objects-values-and-types
[Python Data model: metaclasses]: https://docs.python.org/3/reference/datamodel.html#metaclasses
[PEP 3115]: https://www.python.org/dev/peps/pep-3115/
[Expert Python Porgramming - Second Edition]: https://book.douban.com/subject/26791781/
[什么是metaclass]: http://pyzh.readthedocs.io/en/latest/python-questions-on-stackoverflow.html#id4
[peewee 2.8.5 Model]: https://github.com/coleifer/peewee/blob/2.8.5/peewee.py#L4733
[what is a metaclass in python]: http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python
[深入理解Python中的元类(metaclass)]: http://blog.jobbole.com/21351/

