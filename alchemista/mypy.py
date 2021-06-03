from importlib import import_module
from typing import Any, Callable, Optional, Tuple
from typing import Type as TypingType

from mypy.nodes import AssignmentStmt, CallExpr, NameExpr, StrExpr
from mypy.plugin import FunctionContext, Plugin
from mypy.types import CallableType, Type, TypedDictType
from sqlalchemy.sql import type_api

from alchemista.field import extract_python_type


def infer_from_column_assignment(stmt: AssignmentStmt) -> Tuple[str, TypingType]:
    col_name = stmt.lvalues[0].name
    col_args = stmt.rvalue.args
    if len(col_args) == 1 and isinstance(col_args[0], CallExpr):
        col_args = col_args[0].args
    # TODO: what about a type specified via keyword argument instead of positional?
    col_type_node = col_args[1].node if isinstance(col_args[0], StrExpr) else col_args[0].node
    col_type_module = import_module(col_type_node.module_name)
    try:
        col_type = getattr(col_type_module, col_type_node.name)
        col_type_instance = type_api.to_instance(col_type)
        return col_name, extract_python_type(col_type_instance)
    except AttributeError:
        # TODO: add some warning?
        return col_name, Any


def fields_from_function_callback(ctx: FunctionContext) -> Type:
    if isinstance(ctx.arg_types[0][0], CallableType):
        fields = dict()
        cls = ctx.arg_types[0][0].ret_type.type
        for node in cls.defn.defs.body:
            if (
                isinstance(node, AssignmentStmt)
                and len(node.lvalues) == 1
                and isinstance(node.lvalues[0], NameExpr)
                and not node.lvalues[0].name.startswith("_")
            ):
                attr_name, attr_type = infer_from_column_assignment(node)
                fields[attr_name] = ctx.api.named_type(attr_type.__qualname__)
        fallback = ctx.api.named_type("typing_extensions._TypedDict")
        return TypedDictType(fields, required_keys=set(fields.keys()), fallback=fallback)
    return ctx.default_return_type


class AlchemistaPlugin(Plugin):
    def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], Type]]:
        if fullname == "alchemista.field.fields_from":
            return fields_from_function_callback
        return None


def plugin(version: str) -> TypingType[Plugin]:
    return AlchemistaPlugin
