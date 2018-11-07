---
layout: post
title: 调试技巧-添加属性Hook
tags:
- Python
- debug
---

# 调试技巧-添加属性Hook


### 调试的问题

接手的一个项目中用到了 `mongoengine`，跟踪其中一个 bug。某个 `Document` 子类的对象在调用 `to_json` 时，偶尔会漏掉其中一个字段。

检查 `Document` 源代码发现，`to_json` 实际上是用到了 `_fields_ordered` 属性来生成 `json`，添加日志发现子类的 `_fields_ordered` 属性被修改了，但是代码中找不到修改的地方。

这时候这个问题就难调试了，因为修改的是类的属性，所以一个进程修改了这个属性之后，属性值就变了。但是一个进程要处理很多 `http` 请求，所以有可能是之前某一个请求修改的属性。可能性很多，很难排查。


### 添加属性Hook

为了解决这个问题，只有在修改类属性的时候添加日志，这样就比较容易定位到修改类属性的地方。

```python
class Meta(type):
    def __setattr__(self, name, value):
        print("setattr", name, value, self.__name__)
        super(Meta, self).__setattr__(name, value)

class Test(object, metaclass=Meta):
    _test = ("xxxxx", )

print("before", Test._test)
Test._test = ("xxxxx", "yyyyy")
print("after", Test._test)

```

输出

```
before ('xxxxx',)
setattr _test ('xxxxx', 'yyyyy') Test
after ('xxxxx', 'yyyyy')
```


### 结果

最后定位到问题在于 `pickle.loads` 了老版本的二进制数据，`Document` 类定了 `__setstate__` 方法，在 `loads` 根据数据改变了 `_fields_ordered` 的值。

```python
    def __setstate__(self, data):
        ...
        if '_fields_ordered' in data:
            setattr(type(self), '_fields_ordered', data['_fields_ordered'])
        ...

```

