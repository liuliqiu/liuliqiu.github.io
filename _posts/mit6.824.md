# MIT 6.824 Distributed Systems

https://pdos.csail.mit.edu/6.824/

https://pdos.csail.mit.edu/6.824/schedule.html

## LEC 1 Introduce

https://pdos.csail.mit.edu/6.824/notes/l01.txt

https://pdos.csail.mit.edu/6.824/papers/mapreduce.pdf

http://static.googleusercontent.com/media/research.google.com/zh-CN//archive/mapreduce-osdi04.pdf



### Three big kinds of abstraction that hide distribution from applications.
- Storage.
- Communication.
- Computation.

主题
- 实现
- 性能
- 容错
- 一致性

### MapReduce 

Lec1，Lec2

利用无副作用的函数分解任务，建立通用性的MapReduce模型。

解决分布式执行任务的数据交换问题，容错性，一致性问题。

```
What will likely limit the performance?
network cross-section bandwidth
```


```
Lab 1: MapReduce
Lab 2: replication for fault-tolerance using Raft
Lab 3: fault-tolerant key/value store
Lab 4: sharded key/value store
```

https://pdos.csail.mit.edu/6.824/labs/lab-1.html

### Raft

GFS

Lec3、Lec4、Lec5、Lec6、Lec7

https://pdos.csail.mit.edu/6.824/labs/lab-raft.html

### KV Raft

Lec8、Lec9、Lec10、Lec11

### Sharded KV

Lec12 - Lec22



### MapReduce

- 分布式任务处理，将任务分解到多台机器上执行