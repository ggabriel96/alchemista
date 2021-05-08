from typing import Optional

from sqlalchemy import Column


def infer_python_type(column: Column) -> Optional[type]:
    if hasattr(column.type, "impl"):
        if hasattr(column.type.impl, "python_type"):
            return column.type.impl.python_type
    elif hasattr(column.type, "python_type"):
        return column.type.python_type
    raise RuntimeError(f"Could not infer `python_type` for {column}")
