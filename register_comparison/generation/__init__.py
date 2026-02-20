"""
Rule-based headline-to-canonical transformation system.

This module implements deterministic transformation rules to convert
news headlines (reduced register) to canonical form without using
statistical or machine learning methods.

Includes bidirectional (C→R and R→C) sentence-level transformation.
"""

from .systematicity_analyzer import SystematicityAnalyzer
from .rule_extractor import RuleExtractor
from .transformation_engine import TransformationEngine
from .evaluator import TransformationEvaluator
from .bidirectional_rules import BidirectionalRuleExtractor, RuleSet
from .sentence_transformer import SentenceTransformer
from .constraint_resolver import ConstraintResolver
from .surface_realizer import SurfaceRealizer
from .ngram_scorer import NgramScorer
from .hypothesis_generator import HypothesisGenerator
from .candidate_ranker import CandidateRanker

__all__ = [
    'SystematicityAnalyzer',
    'RuleExtractor',
    'TransformationEngine',
    'TransformationEvaluator',
    'BidirectionalRuleExtractor',
    'RuleSet',
    'SentenceTransformer',
    'ConstraintResolver',
    'SurfaceRealizer',
    'NgramScorer',
    'HypothesisGenerator',
    'CandidateRanker',
]
