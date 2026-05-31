"""Arkheionx guided demo fixtures and workflow helpers."""
from arkheionx.demo.copy import DemoCopyError, copy_demo
from arkheionx.demo.model import Demo
from arkheionx.demo.registry import (
    DEMOS,
    demo_ids,
    fixture_source,
    get_demo,
    list_demos,
    resolve_source_kind,
    workflow_commands,
)
from arkheionx.demo.render import render_commands, render_list, render_show

__all__ = [
    "Demo",
    "DEMOS",
    "DemoCopyError",
    "copy_demo",
    "demo_ids",
    "fixture_source",
    "get_demo",
    "list_demos",
    "render_commands",
    "render_list",
    "render_show",
    "resolve_source_kind",
    "workflow_commands",
]
