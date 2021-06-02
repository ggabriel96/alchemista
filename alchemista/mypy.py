from importlib import import_module
from typing import Any, Callable, Optional, Tuple
from typing import Type as TypingType

from mypy.nodes import AssignmentStmt, NameExpr, StrExpr
from mypy.plugin import FunctionContext, Plugin
from mypy.types import CallableType, Type
from sqlalchemy.sql import type_api

from alchemista.field import extract_python_type


def infer_from_column_assignment(stmt: AssignmentStmt) -> Tuple[str, type]:
    attr_name = stmt.lvalues[0].name
    column_args = stmt.rvalue.args[0].args
    # TODO: what about a type specified via keyword argument instead of positional?
    type_name = column_args[1].node.name if isinstance(column_args[0], StrExpr) else column_args[0].node.name
    type_module_name = stmt.rvalue.args[0].args[0].node.module_name
    type_module = import_module(type_module_name)
    try:
        column_type = getattr(type_module, type_name, None)
        column_type_instance = type_api.to_instance(column_type)
        return attr_name, extract_python_type(column_type_instance)
    except AttributeError:
        # TODO: add some warning?
        return attr_name, Any


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
                fields[attr_name] = attr_type
        # return TypedDictType(fields, required_keys=set(fields.keys()), fallback=None)
    return ctx.default_return_type


class AlchemistaPlugin(Plugin):
    def get_function_hook(self, fullname: str) -> Optional[Callable[[FunctionContext], Type]]:
        if fullname == "alchemista.field.fields_from":
            return fields_from_function_callback
        return None


def plugin(version: str) -> TypingType[Plugin]:
    return AlchemistaPlugin
