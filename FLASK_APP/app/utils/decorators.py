from flask import request, jsonify
from functools import wraps
from pydantic import ValidationError

def validate_input(schema):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            data = request.get_json() or {}
            try:
                validated = schema(**data)
            except ValidationError as e:
                return jsonify({'errors': e.errors()}), 400
            return fn(validated, *args, **kwargs)
        return wrapper
    return decorator