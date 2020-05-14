---
layout: post
title: 从一个mock的bug谈import机制
tags:
- Python
- import
- bug
---



今天修改单元测试时发现一个mock没有生效的问题

(a.py)

```python
def f():
    return 1
```

(main.py)

```python
from unittest.mock import patch, Mock
from a import f

with patch("a.f", Mock(return_value=2)):
    print(f())  # 1
```

像这样，预期调用 `f` 函数的输出是 `2`  ，实际输出是 `1`。最开始我以为是mock用错了，最后发现是对 `import` 的机制了解不够。

把代码修改成下面这样，就能输出 `2` 了。

```python
from unittest.mock import patch, Mock
import a

with patch("a.f", Mock(return_value=2)):
    print(a.f())  # 2
```

为了展示造成这种原因的机制，我写了一个简单的函数

```python
def check_f(module):
    f = getattr(__import__(module), "f", None)
    print(f)
```

然后用这个函数测试了两种机制。

```python
from a import f

check_f("a")             # <function f at 0x110466620>
check_f("__main__")      # <function f at 0x110466620>

with patch("a.f", Mock(return_value=2)):
    check_f("a")         # <Mock id='4565213760'>
    check_f("__main__")  # <function f at 0x110466620>
```

另一种

```python
import a

check_f("a")             # <function f at 0x10e8df598>
check_f("__main__")      # None

with patch("a.f", Mock(return_value=2)):
    check_f("a")         # <Mock id='4536349248'>
    check_f("__main__")  # None
```

无论哪种情况，实际上都已经 `mock` 掉了模块 `a` 中的方法 `f`。问题在于 `from a import f` 在当前函数引入了 `f` 方法，我们调用的是当前模块中的 `f` 方法，这就导致预期的 `mock` 并没有产生效果。而 `import a` 实际上引入的是模块，我们调用的永远是正确的引用。



另外需要特别值得注意的是，从模块中导入子模块与从模块中导入方法的写法完全相同，像这样

```python
from module import sub_module
from module import some_method
```

但是机制是不同的，所以使用的时候需要注意区别。

踩过这个坑之后，我觉得还是尽量导入模块更靠谱些。

