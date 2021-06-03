from importlib import import_module
from typing import Any, Callable, Optional, Tuple
from typing import Type as TypingType

from mypy.errorcodes import CALL_ARG
from mypy.nodes import AssignmentStmt, CallExpr, NameExpr, StrExpr, Node
from mypy.plugin import FunctionContext, Plugin
from mypy.types import CallableType, TupleType, Type, TypedDictType
from sqlalchemy.sql import type_api

from alchemista.field import extract_python_type


def infer_from_column_assignment(stmt: AssignmentStmt) -> TypingType:
    col_args = stmt.rvalue.args
    if len(col_args) == 1 and isinstance(col_args[0], CallExpr):
        col_args = col_args[0].args
    # TODO: what about a type specified via keyword argument instead of positional?
    col_type_node = col_args[1].node if isinstance(col_args[0], StrExpr) else col_args[0].node
    col_type_module = import_module(col_type_node.module_name)
    try:
        col_type = getattr(col_type_module, col_type_node.name)
        col_type_instance = type_api.to_instance(col_type)
        return extract_python_type(col_type_instance)
    except AttributeError:
        # TODO: add some warning?
        return Any


def _column_name(stmt: AssignmentStmt) -> str:
    return stmt.lvalues[0].name


def _is_expected_column_assignment(node: Node) -> bool:
    return (
        isinstance(node, AssignmentStmt)
        and len(node.lvalues) == 1
        and isinstance(node.lvalues[0], NameExpr)
        and not node.lvalues[0].name.startswith("_")
    )


def fields_from_function_callback(ctx: FunctionContext) -> Type:
    if isinstance(ctx.arg_types[0][0], CallableType):
        exclude = ctx.args[1]
        include = ctx.args[2]
        if exclude and include:
            ctx.api.fail("`exclude` and `include` are mutually-exclusive", context=ctx.context, code=CALL_ARG)
        fields = dict()
        cls = ctx.arg_types[0][0].ret_type.type
        field_info_type = ctx.default_return_type.args[-1].items[-1]
        candidate_nodes = (node for node in cls.defn.defs.body if _is_expected_column_assignment(node))
        for node in candidate_nodes:
            attr_name = _column_name(node)
            attr_type = infer_from_column_assignment(node)
            fields[attr_name] = TupleType(
                [ctx.api.named_type(attr_type.__qualname__), field_info_type],
                fallback=ctx.api.named_type("builtins.tuple"),
            )
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
