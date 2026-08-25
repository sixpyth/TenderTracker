import inspect
from typing import Optional
from pydantic import BaseModel


def optional(*fields):
    def dec(_cls):
        # Pydantic v2 compatibility
        if hasattr(_cls, "model_fields"):
            fields_dict = _cls.model_fields
            for field in target_fields:
                if field in fields_dict:
                    field_info = fields_dict[field]
                    field_info.default = None
                    if field_info.annotation is not None:
                        field_info.annotation = Optional[field_info.annotation]
            _cls.model_rebuild(force=True)
            return _cls

        # Pydantic v1 compatibility fallback
        fields_dict = getattr(_cls, "__fields__", {})
        for field in target_fields:
            if field in fields_dict:
                f = fields_dict[field]
                if hasattr(f, "required"):
                    f.required = False
                if hasattr(f, "default"):
                    f.default = None
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        if hasattr(cls, "model_fields"):
            target_fields = list(cls.model_fields.keys())
        else:
            target_fields = list(getattr(cls, "__fields__", {}).keys())
        return dec(cls)
    else:
        target_fields = list(fields)
        return dec
