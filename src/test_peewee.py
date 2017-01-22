
class FieldDescriptor(object):
    def __init__(self, field):
        self.field = field
        self.att_name = self.field.name

    def __get__(self, instance, instance_type = None):
        if instance is not None:
            return instance._data.get(self.att_name)
        return self.field

    def __set__(self, instance, value):
        instance._data[self.att_name] = value


class Field(object):
    def add_to_class(self, model_class, name):
        self.name = name
        model_class._fields.append(self)
        setattr(model_class, name, FieldDescriptor(self))


class BaseModel(type):
    inheritable = set([])

    def __new__(cls, name, bases, attrs):
        cls = super(BaseModel, cls).__new__(cls, name, bases, attrs)
        if name == "Model":
            return cls

        cls._fields = []
        cls._data = None
        cls._name = name.lower()
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                attr.add_to_class(cls, name)
        return cls


class Model(metaclass=BaseModel):
    def __init__(self, *args, **kwargs):
        self._data = {}
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def select(cls):
        fields= ", ".join(field.name for field in cls._fields)
        sql = "SELECT ({fields}) FROM {table_name}".format(table_name=cls._name, fields=fields)
        for data in cls.Meta.db.execute(sql):
            yield cls(**{field.name:value for field, value in zip(cls._fields, data)})


import sqlite3
class User(Model):
    name = Field()
    class Meta(object):
        db = sqlite3.Connection("user.db")

for user in User.select():
    print(user.name)
