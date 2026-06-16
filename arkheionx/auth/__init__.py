"""Authorization and signature-binding analysis."""
from __future__ import annotations

from .models import AuthorizationAnalysis
from .signature_detector import analyze_authorization

__all__ = ["AuthorizationAnalysis", "analyze_authorization"]
