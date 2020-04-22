---
layout: post
title: lua源码笔记-string
tags:
- lua
- note
---

### 结构

lua 中 string 分成两种 short string 和 long string，两者都使用 `TString ` 结构存储数据，两者的 tag 都为`LUA_TSTRING`，而 variant 分别为1和2。

([lobject.h](https://github.com/lua/lua/blob/v5.4-beta/lobject.h#L313-L315))

```c
/* Variant tags for strings */
#define LUA_TSHRSTR	(LUA_TSTRING | (1 << 4))  /* short strings */
#define LUA_TLNGSTR	(LUA_TSTRING | (2 << 4))  /* long strings */
```

([lobject.h](https://github.com/lua/lua/blob/v5.4-beta/lobject.h#L337-L350))

```c
/*
** Header for string value; string bytes follow the end of this structure
** (aligned according to 'UTString'; see next).
*/
typedef struct TString {
  CommonHeader;
  lu_byte extra;  /* reserved words for short strings; "has hash" for longs */
  lu_byte shrlen;  /* length for short strings */
  unsigned int hash;
  union {
    size_t lnglen;  /* length for long strings */
    struct TString *hnext;  /* linked list for hash table */
  } u;
} TString;
```

其中 short string 保存在一个类型为 `stringtable` 的哈希表中，利用了结构中的 `hnext ` 形成链表结构。而 long string 不需要这个指针，利用这部分存储长度 `lnglen`。short string 的长度则存储在 `shrlen` 中， `shrlen`是8位，因为 short string 保存40位以下的字符串，而 `lnglen` 是64位的。`hash` 部分用来存储字符串的hash值。而`extra`部分则用途特殊，留在后面说。

整个`TString`结构中没有存储字符串的内容，字符串的内容使用一个 `char *`指针紧跟在 `TString`结构后面。

([lobject.h](https://github.com/lua/lua/blob/v5.4-beta/lobject.h#L354-L359))

```c
/*
** Get the actual string (array of bytes) from a 'TString'.
** (Access to 'extra' ensures that value is really a 'TString'.)
*/
#define getstr(ts)  \
  check_exp(sizeof((ts)->extra), cast_charp((ts)) + sizeof(TString))
```

`cast_charp` 将 `ts` 转换为 `char *` 类型，加上 `sizeof(TString)` 将指针移到 `TString` 结构后面。

### 新建字符串

([lstring.c](https://github.com/lua/lua/blob/v5.4-beta/lstring.c#L228-L242))

```c
/*
** new string (with explicit length)
*/
TString *luaS_newlstr (lua_State *L, const char *str, size_t l) {
  if (l <= LUAI_MAXSHORTLEN)  /* short string? */
    return internshrstr(L, str, l);
  else {
    TString *ts;
    if (unlikely(l >= (MAX_SIZE - sizeof(TString))/sizeof(char)))
      luaM_toobig(L);
    ts = luaS_createlngstrobj(L, l);
    memcpy(getstr(ts), str, l * sizeof(char));
    return ts;
  }
}
```

如果字符串长度小于等于 `LUAI_MAXSHORTLEN`（40）时，调用 `intershrstr`创建短字符串。

否则先检查长度是否超过上限。然后创建`TString`结构，最后将字符串复制到 `TString`结构后面。

```c
#define sizelstring(l)  (sizeof(TString) + ((l) + 1) * sizeof(char))
```

### long string

([lstring.c](https://github.com/lua/lua/blob/v5.4-beta/lstring.c#L150-L171))

```c
/*
** creates a new string object
*/
static TString *createstrobj (lua_State *L, size_t l, int tag, unsigned int h) {
  TString *ts;
  GCObject *o;
  size_t totalsize;  /* total size of TString object */
  totalsize = sizelstring(l);
  o = luaC_newobj(L, tag, totalsize);
  ts = gco2ts(o);
  ts->hash = h;
  ts->extra = 0;
  getstr(ts)[l] = '\0';  /* ending 0 */
  return ts;
}


TString *luaS_createlngstrobj (lua_State *L, size_t l) {
  TString *ts = createstrobj(L, l, LUA_TLNGSTR, G(L)->seed);
  ts->u.lnglen = l;
  return ts;
}
```

这里可以看到 `createstrobj` 先计算了需要的内存，然后调用 `luaC_newobj` 分配内存并设置 `tag` 值，然后设置了 `extra` 为0，并设置了 `TString` 之后的字符串末尾为 `'\0'`，而 `luaS_createlngstrobj` 则设置了 `lnglen`。

需要特别注意到，这里将 `hash` 设置成了 `G(L)->seed`，这里是全局的随机种子，并不是这个字符串的 `hash` 值，因为 `long string` 并不需要立即使用它的 `hash` 值，所以只在需要hash值时才生出。

([lstring.c](https://github.com/lua/lua/blob/v5.4-beta/lstring.c#L62-L69))

```c
unsigned int luaS_hashlongstr (TString *ts) {
  lua_assert(ts->tt == LUA_TLNGSTR);
  if (ts->extra == 0) {  /* no hash? */
    ts->hash = luaS_hash(getstr(ts), ts->u.lnglen, ts->hash);
    ts->extra = 1;  /* now it has its hash */
  }
  return ts->hash;
}
```

`luaS_hashlongstr` 用来生成 long string 的哈希值，这里可以看到当 `long string` 的 `extra` 为 0 时，先使用字符串、长度和随机种子生出hash值，然后将 `extra` 置为 `1` ，这样下次就不用再次生出 `hash` 值了。



### short string

然后看看创建 short string 的逻辑，所有的short string 会保存在一个全局的`stringtabhle`中。

([lstate.h](https://github.com/lua/lua/blob/v5.4-beta/lstate.h#L159-L163))

```c
typedef struct stringtable {
  TString **hash;
  int nuse;  /* number of elements */
  int size;
} stringtable;

typedef struct global_State {
  // ...
  stringtable strt;  /* hash table for strings */
  // ...
} global_State;
```

`stringtable` 包括三个字段，hash 是一个 `TString` 链表的数组，`nuse` 表示其中字符串数量，`size` 为数组长度。

([lstring.c](https://github.com/lua/lua/blob/v5.4-beta/lstring.c#L195-L225))

```c
/*
** Checks whether short string exists and reuses it or creates a new one.
*/
static TString *internshrstr (lua_State *L, const char *str, size_t l) {
  TString *ts;
  global_State *g = G(L);
  stringtable *tb = &g->strt;
  unsigned int h = luaS_hash(str, l, g->seed);
  TString **list = &tb->hash[lmod(h, tb->size)];
  lua_assert(str != NULL);  /* otherwise 'memcmp'/'memcpy' are undefined */
  for (ts = *list; ts != NULL; ts = ts->u.hnext) {
    if (l == ts->shrlen && (memcmp(str, getstr(ts), l * sizeof(char)) == 0)) {
      /* found! */
      if (isdead(g, ts))  /* dead (but not collected yet)? */
        changewhite(ts);  /* resurrect it */
      return ts;
    }
  }
  /* else must create a new string */
  if (tb->nuse >= tb->size) {  /* need to grow string table? */
    growstrtab(L, tb);
    list = &tb->hash[lmod(h, tb->size)];  /* rehash with new size */
  }
  ts = createstrobj(L, l, LUA_TSHRSTR, h);
  memcpy(getstr(ts), str, l * sizeof(char));
  ts->shrlen = cast_byte(l);
  ts->u.hnext = *list;
  *list = ts;
  tb->nuse++;
  return ts;
}
```

1. 先计算了字符串的哈希值 `h`
2. 然后去全局的哈希表 `global_State.strt` 中查找，找到了直接返回
3. 没有找到时，先根据需要调整哈希表的大小。
4. 然后分配新字符串的内存空间，设置字符串内容和长度。
5. 然后将字符串加入到全局哈希表中
6. 最后调整全局哈希表中的对象数量

之前已经看过了 `extra` 字段在 long string 用来标记是否已经生成哈希值，而在 short string 则是用来标记关键字。

（[llex.c](https://github.com/lua/lua/blob/v5.4-beta/llex.c#L39-L79))

```c
/* ORDER RESERVED */
static const char *const luaX_tokens [] = {
    "and", "break", "do", "else", "elseif",
    "end", "false", "for", "function", "goto", "if",
    "in", "local", "nil", "not", "or", "repeat",
    "return", "then", "true", "until", "while",
    "//", "..", "...", "==", ">=", "<=", "~=",
    "<<", ">>", "::", "<eof>",
    "<number>", "<integer>", "<name>", "<string>"
};

void luaX_init (lua_State *L) {
  int i;
  TString *e = luaS_newliteral(L, LUA_ENV);  /* create env name */
  luaC_fix(L, obj2gco(e));  /* never collect this name */
  for (i=0; i<NUM_RESERVED; i++) {
    TString *ts = luaS_new(L, luaX_tokens[i]);
    luaC_fix(L, obj2gco(ts));  /* reserved words are never collected */
    ts->extra = cast_byte(i+1);  /* reserved word */
  }
}
```

在初始化阶段，会把所有关键字字符串都建好，然后把 `extra`设为正整数。这样在语法分析时就能通过`extra`来判断一个字符串是否为关键字。

([lstring.h](https://github.com/lua/lua/blob/v5.4-beta/lstring.h#L31))

```c
#define isreserved(s)	((s)->tt == LUA_TSHRSTR && (s)->extra > 0)
```

### 缓存

最后 lua 还为字符串做了一层缓存。

([lstring.c](https://github.com/lua/lua/blob/v5.4-beta/lstring.c#L245-L265))

```c
/*
** Create or reuse a zero-terminated string, first checking in the
** cache (using the string address as a key). The cache can contain
** only zero-terminated strings, so it is safe to use 'strcmp' to
** check hits.
*/
TString *luaS_new (lua_State *L, const char *str) {
  unsigned int i = point2uint(str) % STRCACHE_N;  /* hash */
  int j;
  TString **p = G(L)->strcache[i];
  for (j = 0; j < STRCACHE_M; j++) {
    if (strcmp(str, getstr(p[j])) == 0)  /* hit? */
      return p[j];  /* that is it */
  }
  /* normal route */
  for (j = STRCACHE_M - 1; j > 0; j--)
    p[j] = p[j - 1];  /* move out last element */
  /* new element is first in the list */
  p[0] = luaS_newlstr(L, str, strlen(str));
  return p[0];
}
```

这个缓存是一个二维数组，通过对字符串指针的地址取模，决定缓存数组的第一个下标，然后在剩下的一维数组中遍历比较，找到则直接返回，如果没有找到，会在生成字符串对象后插入缓存一维数组的最前列。
