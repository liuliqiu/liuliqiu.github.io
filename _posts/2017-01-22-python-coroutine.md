---
layout: post
title: Python协程coroutine
tags:
- Python
---

## 协程

1. 进程，独立内存空间。
2. 线程，共享内存空间，抢占式。
3. 协程，共享内存空间，非抢占式。

解决CPU/Memory资源、I/O资源瓶颈冲突问题。
当前协程因为I/O资源限制无法执行下去时，释放CPU/Memory资源让给其他协程。

协程的定义
回调没有保存上下文
事件循环、让出调度CPU资源

Generators - semicoroutines
Communicating sequential processes
continuation    保存当前上下文

### 协程的优点
不用切换上下文


### 协程的实现


### python中的协程

- 2.5 generator
- 3.3 yield from
- 3.4 asyncio
- 3.5 async/await

