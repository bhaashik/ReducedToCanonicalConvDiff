"""
Rule-based headline-to-canonical transformation system.

This module implements deterministic transformation rules to convert
news headlines (reduced register) to canonical form without using
statistical or machine learning methods.
"""

from .systematicity_analyzer import SystematicityAnalyzer
from .rule_extractor import RuleExtractor
from .transformation_engine import TransformationEngine
from .evaluator import TransformationEvaluator

__all__ = [
    'SystematicityAnalyzer',
    'RuleExtractor',
    'TransformationEngine',
    'TransformationEvaluator'
]
