#!/usr/bin/env python3
"""
Configuration for Tree Edit Distance algorithms.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TEDConfig:
    """Configuration for Tree Edit Distance calculation."""

    # Available algorithms
    AVAILABLE_ALGORITHMS = ['simple', 'zhang_shasha', 'klein', 'rted']

    # Default algorithms to use
    enabled_algorithms: List[str] = None

    # Performance optimization settings
    use_memoization: bool = True
    max_tree_size_for_complex_algorithms: int = 50

    # Algorithm-specific settings
    zhang_shasha_enabled: bool = True
    klein_enabled: bool = True
    rted_enabled: bool = True
    simple_enabled: bool = True

    def __post_init__(self):
        """Initialize enabled algorithms based on individual flags."""
        if self.enabled_algorithms is None:
            self.enabled_algorithms = []

            if self.simple_enabled:
                self.enabled_algorithms.append('simple')
            if self.zhang_shasha_enabled:
                self.enabled_algorithms.append('zhang_shasha')
            if self.klein_enabled:
                self.enabled_algorithms.append('klein')
            if self.rted_enabled:
                self.enabled_algorithms.append('rted')

        # Validate algorithms
        for alg in self.enabled_algorithms:
            if alg not in self.AVAILABLE_ALGORITHMS:
                raise ValueError(f"Unknown TED algorithm: {alg}")

    @classmethod
    def default(cls):
        """Create default configuration with all algorithms enabled."""
        return cls()

    @classmethod
    def simple_only(cls):
        """Create configuration with only simple algorithm."""
        return cls(
            simple_enabled=True,
            zhang_shasha_enabled=False,
            klein_enabled=False,
            rted_enabled=False
        )

    @classmethod
    def standard_only(cls):
        """Create configuration with only standard algorithms (no simple)."""
        return cls(
            simple_enabled=False,
            zhang_shasha_enabled=True,
            klein_enabled=True,
            rted_enabled=True
        )

    @classmethod
    def performance_optimized(cls):
        """Create configuration optimized for performance."""
        return cls(
            simple_enabled=True,
            zhang_shasha_enabled=False,  # Most expensive
            klein_enabled=True,          # Good memoization
            rted_enabled=True,           # Adaptive algorithm
            max_tree_size_for_complex_algorithms=30
        )

    def get_algorithms_for_tree_size(self, tree_size: int) -> List[str]:
        """Get appropriate algorithms based on tree size."""
        if tree_size > self.max_tree_size_for_complex_algorithms:
            # For large trees, use only fast algorithms
            fast_algorithms = ['simple', 'rted']
            return [alg for alg in self.enabled_algorithms if alg in fast_algorithms]
        else:
            # For small trees, use all enabled algorithms
            return self.enabled_algorithms[:]

    def get_algorithm_description(self, algorithm: str) -> str:
        """Get human-readable description of algorithm."""
        descriptions = {
            'simple': 'Simple String-based Distance',
            'zhang_shasha': 'Zhang-Shasha Dynamic Programming',
            'klein': 'Klein Memoized Tree Edit Distance',
            'rted': 'Robust Tree Edit Distance (RTED)'
        }
        return descriptions.get(algorithm, algorithm)

    def get_algorithm_mnemonic(self, algorithm: str) -> str:
        """Get short mnemonic for algorithm."""
        mnemonics = {
            'simple': 'SIMP',
            'zhang_shasha': 'ZSHA',
            'klein': 'KLEN',
            'rted': 'RTED'
        }
        return mnemonics.get(algorithm, algorithm[:4].upper())


# Global default configuration
DEFAULT_TED_CONFIG = TEDConfig.default()

# Predefined configurations for common use cases
CONFIGS = {
    'default': TEDConfig.default(),
    'simple_only': TEDConfig.simple_only(),
    'standard_only': TEDConfig.standard_only(),
    'performance': TEDConfig.performance_optimized()
}


def get_ted_config(config_name: str = 'default') -> TEDConfig:
    """Get TED configuration by name."""
    if config_name in CONFIGS:
        return CONFIGS[config_name]
    else:
        raise ValueError(f"Unknown TED configuration: {config_name}. Available: {list(CONFIGS.keys())}")