"""Scope parsing for the lens layer.

The lens layer reuses the v7 markdown scope parser verbatim — a scope note is a
scope note regardless of which protocol lens reads it. This module re-exports the
v7 parser so lens code has a single, local import site.
"""
from __future__ import annotations

from arkheionx.scope_orchestration.scope_parser import (
    empty_scope,
    parse_scope_file,
    parse_scope_text,
    requires_medium_high,
)

__all__ = ["parse_scope_file", "parse_scope_text", "empty_scope", "requires_medium_high"]
