---
layout: post
title: Python日志模块logging
tags:
- Python
---

# 简介

Python从2.3开始提供了logging模块用于纪录调试信息、运行状况、警告和报错等日志信息。
当程序崩溃或者出错时，我们需用日志定位问题。分析程序日常运行状况。
Python的logging模块从很多日志系统中吸取了经验，是了一个非常灵活的日志系统。
logging模块的使用很简单：

```python
import logging
logging.info("just a message")
logging.warning("this is a warning message")
```

这样就会输出一条 `"WARNING:root:this is a warning message"` 的警告消息，但是 `"just a message"` 并不会被输出，因为logging模块有日志级别。

# 日志级别
logging模块使用级别来标示日志的严重程度，logging模块中提供了`DEBUG(10)` 、 `INFO(20)`、 `WARNING(30)`、 `ERROR(40)`、 `CRITICAL(50)`从轻到重的五个默认日志级别，并且可以使用数值自定义日志级别。可以通过函数设置只处理一定级别以上的日志，默认只处理`WARNING`及以上级别的日志。

```python
import logging
logging.basicConfig(level=logging.INFO)
logging.info("just a message")
logging.log(23, "a custom message")
logging.addLevelName(23, "CUSTOM")
logging.log(23, "a custom message")
```

这样就会输出两条日志消息 `"INFO:root:just a message"` 和 `"CUSTOM:root:a custom message"`。  
注意`basicConfig`必须在第一条日志信息输出前调用，否则就会直接使用默认的配置，不会配置成功。  

# Handler
默认日志会输出到stderr，但是我可以使用Handler更灵活的处理日志。
```python
# Python 3.3+ basicConfig才有handlers参数，较低版本的Python本示例运行结果使用默认配置输出到stderr
import logging
import sys
handlers = (logging.FileHandler("some.log"), logging.StreamHandler(sys.stdout))
logging.basicConfig(handlers=handlers)
logging.warning("warning message")
```
这样日志就可以同时输出到日志文件和stdout。Python在子模块[logging.handlers][Library logging.handlers]中提供了大量的Handler类，用于以不同的方式处理日志。  

| Handler |  说明|
| ------  | ------ |
| StreamHandler | 将日志输出到流中，比如stdout、stderr、file-like object |
| FileHandler | 将日志输出到文件中 |
| NullHandler | 不输出日志、用于库开发者设置默认日志Handler | Python3.1+|
| WatchedFileHandler | 当日志文件被修改时，重新打开日志文件的FileHandler |
| RotatingFileHandler | 当日志文件达到maxBytes时重命名原有日志文件，新打开一个日志文件输出 |
| TimeRotatingFileHandler | 按时间轮转日志文件 |
| SocketHandler | 将日志通过TCP协议输出 |
| DatagramHandler | 将日志通过UDP协议输出 |
| SysLogHandler | 将日志输出到Unix的syslog |
| NTEventLogHandler | 将日志输出到Windows的日志服务 |
| SMTPHandler | 通过邮件的方式输出日志 |
| MemoryHandler | 将日志暂存在内存中，然后周期性的将日志传入到target中 |
| HTTPHandler | 通过HTTP请求的方式输出日志 |
| QueueHandler | 将请求输出到一个队列中，然后使用QueueListener监听队列将日志传递给其他Handler | Python3.2+ |

这些Handler包括了各种各样的输出方式，另外还有MemoryHandler和QueueHandler可以与其他的Handler搭配实现非常灵活的日志处理。

# Formatter
logging中为每一条日志都生成一个[LogRecord]对象实例，并且提供了Formatter类去将一个LogRecord实例转化为文本。我们需要给Formatter类传递一个格式化字符串，Formatter使用LogRecord实例的属性去格式化字符串。LogRecord对象有提供[非常多的属性][LogRecord attributes]可以用于格式化字符串。

```python
import logging
import sys
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)s %(funcName)s: %(message)s")
handler.setFormatter(formatter)
logging.basicConfig(handlers=(handler, ))
def do_something():
    logging.warning("warning message")
do_something()
```

会输出 `"WARNING 2016-12-21 01:39:57,694 root do_something: warning message"`

# Logger
在我们上面的所有例子中都会输出root，从上面的例子可以看到这是LogRecord.name。  
实际上这个name代表着Logger实例的名字，logging模块中提供了`logging.getLogger`函数来通过名字获取对应的Logger实例。使用Logger实例来区分不同的日志来源，对于每个相同名字的日志来源维护唯一实例。  
另外通过点分割来形成树形的命名空间。比如说`logging.getLogger("one")`就是`logging.getLogger("one.two")`的父Logger，并且有一个唯一的RootLogger作为默认的的Logger。每个Logger都会将处理玩的LogRecord抛给他的父Logger。  
- Logger类提供了`debug`, `info`, `warning`, `error`, `critical`, `log`, `exception`等方法用于创建LogRecord实例。
- Logger类提供了`setLevel`方法用于设置最低处理的日志等级。
- Logger类提供了`addHandler`, `removeHandler`方法用于处理日志。
- Logger类提供了`addFilter`, `removeFIlter`方法用于过滤日志。

```python
import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)s %(funcName)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class Logic(object):
    logger = logging.getLogger("logic")

    def do_something(self):
        self.logger.info("do something")

def do_everything():
    logic = Logic()
    logger.info("start doing everything")
    logic.do_something()
    logger.info("everything done")

do_everything()
```

[Logging HOWTO]中的这张图很好的说明了loggin模块的整个日志处理体系。

![logging flow](https://docs.python.org/3/_images/logging_flow.png)


# 参考资料

- [Logging HOWTO]
- [Library logging]
- [logging cookbook]
- [PEP 282]



[PEP 282]: https://www.python.org/dev/peps/pep-0282/
[Logging HOWTO]: https://docs.python.org/3/howto/logging.html
[logging cookbook]: https://docs.python.org/3/howto/logging-cookbook.html
[Library logging]: https://docs.python.org/3/library/logging.html
[Library logging.config]: https://docs.python.org/3/library/logging.config.html
[Library logging.handlers]: https://docs.python.org/3/library/logging.handlers.html
[LogRecord]: https://docs.python.org/3/library/logging.html#logging.LogRecord
[LogRecord attributes]: https://docs.python.org/3/library/logging.html#logrecord-attributes
