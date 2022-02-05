#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import inspect
import typing
import dacite
from deepdiff import DeepDiff
from contextlib import suppress
from functools import wraps
from dataclasses import dataclass, asdict

ELASTICSEARCH = "elasticsearch"
KIBANA = "kibana"
RESOURCE_TYPES = (ELASTICSEARCH, KIBANA)


def enforce_types(callable):
    spec = inspect.getfullargspec(callable)

    def check_types(*args, **kwargs):
        parameters = dict(zip(spec.args, args))
        parameters.update(kwargs)
        for name, value in parameters.items():
            with suppress(KeyError):  # Assume un-annotated parameters can be any type
                type_hint = spec.annotations[name]
                if isinstance(type_hint, typing._SpecialForm):
                    # No check for typing.Any, typing.Union, typing.ClassVar (without parameters)
                    continue
                try:
                    actual_type = type_hint.__origin__
                except AttributeError:
                    # In case of non-typing types (such as <class 'int'>, for instance)
                    actual_type = type_hint
                # In Python 3.8 one would replace the try/except with
                # actual_type = typing.get_origin(type_hint) or type_hint
                if isinstance(actual_type, typing._SpecialForm):
                    # case of typing.Union[…] or typing.ClassVar[…]
                    actual_type = type_hint.__args__
                try:
                    if not isinstance(value, actual_type):
                        raise TypeError(
                            "Unexpected type for '{}' (expected {} but found {})".format(
                                name, type_hint, type(value)
                            )
                        )
                except TypeError as e:
                    raise TypeError(
                        f"{e}\n arg1(value)={value}, arg2(actual_type)={actual_type}"
                    )

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            check_types(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    if inspect.isclass(callable):
        callable.__init__ = decorate(callable.__init__)
        return callable

    return decorate(callable)


@dataclass(frozen=True)
class BaseResource:
    def asdict(self):
        return asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )

    def to_json(self):
        return json.dumps(self.asdict(), indent=4)

    @classmethod
    def fromdict(cls, schemaclass, body):
        schema = schemaclass()
        result = schema.load(body)
        return dacite.from_dict(data_class=cls, data=result)

    @property
    def stack_type(self):
        module = self.__module__
        for _type in RESOURCE_TYPES:
            if _type in module:
                return _type

    def diff(self, resource):
        try:
            obj = resource.asdict()
        except AttributeError:
            obj = {}

        return DeepDiff(self.asdict(), obj, view="tree")

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.id})"
