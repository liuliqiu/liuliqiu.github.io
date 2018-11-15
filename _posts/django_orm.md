# django orm

### [tips](https://blog.csdn.net/orangleliu/article/details/57088557) 

1. 习惯隔离代码并记录产生的查询

2. 不要在循环中查询
3. 了解 ORM 是怎么缓存数据的
4. 知道 Django 何时会做查询
5. 不要以牺牲清晰度为代价过度优化

### QuerySet

DJango orm 转为 mysql 的基础在于 django.db.models.QuerySet 类，每个 QuerySet 实例对应一个 mysql 查询语句。

```Python
def queryset_to_sql(queryset):
    return queryset.query.get_compiler(using=queryset.db).as_sql()
queryset_to_sql(GameZone.objects.all())
```

默认QuerySet 类会把表的所有字段查询出来，但有时我们只需要其中的部分字段，有两个方法 values 和 values_list可以实现只查询某些指定字段。

```Python
queryset_to_sql(GameZone.objects.values("name", "display_order").all())
queryset_to_sql(GameZone.objects.values_list("name", "display_order").all())
```


### 查询与缓存
QuerySet 在 `__len__`,`__iter__`, `__bool__` 三种情况下会去做查询。每个QuerySet 查询后都会缓存结果。

QuerySet.count, QuerySet.exists 方法在实例有缓存时，会优先使用缓存结果，否则会构造一个优化的 QuerySet去查询数据库。

```python
class QuerySet(object):
    def __init__(self, ...):
        self._result_cache = None
        self._iterable_class = ModelIterable
    
    def __len__(self):
        self._fetch_all()
        return len(self._result_cache)
    
    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)
    
    def __bool__(self):
        self._fetch_all()
        return bool(self._result_cache)
    
    def _fetch_all():
        if self._result_cache is None:
            self._result_cache = list(self._iterable_class(self))
        if self._prefetch_related_lookups and not self._prefetch_done:
            self._prefetch_related_objects()

    def __getitem__(self, k):
        if self._result_cache is not None:
            return self._result_cache[k]

        if isinstance(k, slice):
            qs = self._clone()
            qs.query.set_limits(start, stop)
            return list(qs)[::k.step] if k.step else qs

        qs = self._clone()
        qs.query.set_limits(k, k + 1)
        return list(qs)[0]
        
    def _clone(self, **kwargs):
        query = self.query.clone()
        clone = self.__class__(model=self.model, query=query, using=self._db, hints=self._hints)
        clone.__dict__.update(kwargs)
        return clone
        
    def count(self):
        if self._result_cache is not None:
            return len(self._result_cache)
        return self.query.get_count(using=self.db)
        
    def exists(self):
        if self._result_cache is None:
            return self.query.has_results(using=self.db)
        return bool(self._result_cache)
        
    def first(self):
        """
        Returns the first object of a query, returns None if no match is found.
        """
        objects = list((self if self.ordered else self.order_by('pk'))[:1])
        if objects:
            return objects[0]
        return None
    def iterator(self):
        use_chunked_fetch = not connections[self.db].settings_dict.get('DISABLE_SERVER_SIDE_CURSORS')
        return iter(self._iterable_class(self, chunked_fetch=use_chunked_fetch))
```

### 来自 django官方的[数据库优化建议](https://docs.djangoproject.com/en/1.11/topics/db/optimization/)


1. Profile first
2. Use standard DB optimization techniques
    * 索引
    * Appropriate use of field types.
3. Understand QuerySets
    * Understand QuerySet are lazy
    * Understand when QuerySet are evaluated
    * Understand how the data is held in memory
    * Understand cached attributes
    * Use the with template tag
    * Use iterator()
5. Do database work in the database rather than in Python
    * use filter and exclude to do filtering in the database.
    * Use F expressions to filter based on other fields within the same model.
    * Use annotate to do aggregation in the database.
    * Use raw SQL
6. Retrieve individual objects using a unique, indexed column
    * Use QuerySet.select_related() and prefetch_related()
7. Retrieve everything at once if you know you will need it, Don’t retrieve things you don’t need
    * Use QuerySet.values() and values_list()
    * Use QuerySet.defer() and only()
    * Use QuerySet.count()
    * Use QuerySet.exists()
    * Don’t overuse count() and exists()
    * Use QuerySet.update() and delete()
    * Use foreign key values directly
    * Don’t order results if you don’t care
8. Insert in bulk

