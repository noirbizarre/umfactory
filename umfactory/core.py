from faker import Faker
from marshmallow import missing
from umongo import fields

fake = Faker()


DEFAULT_TYPES = {
    fields.StrField: fake.word,
    fields.StringField: fake.word,
    fields.UUIDField: fake.uuid4,
    fields.NumberField: fake.pyint,
    fields.IntegerField: fake.pyint,
    fields.IntField: fake.pyint,
    fields.DecimalField: fake.pydecimal,
    fields.BoolField: fake.pybool,
    fields.BooleanField: fake.pybool,
    fields.FloatField: fake.pyfloat,
    fields.DateTimeField: fake.date_time,
    fields.LocalDateTimeField: fake.date_time,
    # fields.TimeField: fake.time_object,
    # fields.DateField: fake.date_object,
    fields.URLField: fake.url,
    fields.UrlField: fake.url,
    fields.EmailField: fake.email,
    # fields.FormattedString
    # fields.TimeDelta
    # fields.Dict
    # fields.Method
    # fields.Function
    # fields.Constant
}


class FactoryMetaClass(type):
    def __new__(mcs, class_name, bases, attrs):

        attrs_meta = attrs.pop('Meta', None)
        attrs_params = attrs.pop('Params', None)

        meta = MetaFactory(attrs_meta, attrs_params)
        attrs['_meta'] = meta

        new_class = super(FactoryMetaClass, mcs).__new__(mcs, class_name, bases, attrs)

        return new_class

    def __str__(cls):
        if cls._meta.abstract:
            return '<%s (abstract)>' % cls.__name__
        else:
            return '<%s for %s>' % (cls.__name__, cls._meta.model)


class MetaFactory:
    abstract = False
    model = None

    def __init__(self, meta, params):
        meta = vars(meta) if meta else {}
        for key, value in meta.items():
            if not key.startswith('_'):
                setattr(self, key, value)

        if self.model is None:
            self.abstract = True


class Factory(metaclass=FactoryMetaClass):
    @classmethod
    async def create(cls, **kwargs):
        schema = cls._meta.model.schema

        obj = cls._meta.model(**kwargs)

        for name, field in schema.fields.items():
            if obj._data.get(name) == missing and field.required:
                obj._data.set(name, DEFAULT_TYPES[field.__class__]())

        await obj.commit()
        return obj
