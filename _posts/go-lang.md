# golang 

## 基础

#### 类型

静态，强类型

分为值类型和引用类型，值类型传递时为复制传递

1. 值类型
   1. 基本类型
      1. 数字 (numbers)
      2. 字符串 (strings)
      3. 布尔型 (booleans)
   2. 聚合类型
      1. 数组 (arrays)
      2. 结构 (structs)
2. 引用类型
   1. 指针 (pointers)
   2. 切片 (slices)
   3. 映射 (maps)
   4. 函数 (functions)
   5. 通道 (channels)

Arrays 定长，值类型。

Slices 变长，底层是Arrays。

Struct Embedding，Anonymous Fields

#### 流程

if、switch、for、

defer function call

#### 函数

first-class values、闭包

multiple return values

Anonymous Functions

#### struct 

duck type interface、method

methods pointer receiver & type receiver

Composing Types by Struct Embedding

interface concrete type、 concrete value

#### goroutine

go channel、CSP、sync

buffered channels

Unbuffered channels

Multiplexing with select

sync

1. Mutex
2. RWMutex
3. Once
4. WaitGroup

### reflect & unsafe

