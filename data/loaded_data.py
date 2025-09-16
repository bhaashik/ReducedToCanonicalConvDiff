from pathlib import Path
from typing import List, Dict, Any
from conllu import TokenList
from nltk.tree import Tree
import sys
import os

# Add parent directory to path to import from register_comparison
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from register_comparison.readers.readers import read_plain_text, read_conllu, read_constituency
from paths_config import TEXT_FILES, CONLLU_FILES, CONST_FILES, NEWSPAPERS


class LoadedData:
    """
    Loads and stores all data files (text, dependency, constituency) for register comparison.
    Provides centralized access to loaded data for all newspapers and registers.
    """

    def __init__(self):
        # Initialize empty data containers
        self.text_data: Dict[str, Dict[str, List[str]]] = {}
        self.dependency_data: Dict[str, Dict[str, List[TokenList]]] = {}
        self.constituency_data: Dict[str, Dict[str, List[Tree]]] = {}

        # Track what's been loaded
        self.loaded_newspapers: List[str] = []
        self.is_loaded = False

    def load_all_data(self):
        """Load data for all newspapers and registers."""
        for newspaper in NEWSPAPERS:
            self.load_newspaper_data(newspaper)
        self.is_loaded = True
        print(f"Loaded data for {len(self.loaded_newspapers)} newspapers")

    def load_newspaper_data(self, newspaper_name: str):
        """Load data for a specific newspaper."""
        if newspaper_name not in NEWSPAPERS:
            raise ValueError(f"Unknown newspaper: {newspaper_name}. Available: {NEWSPAPERS}")

        if newspaper_name in self.loaded_newspapers:
            print(f"Data for {newspaper_name} already loaded")
            return

        print(f"Loading data for {newspaper_name}...")

        # Initialize data structures for this newspaper
        self.text_data[newspaper_name] = {}
        self.dependency_data[newspaper_name] = {}
        self.constituency_data[newspaper_name] = {}

        # Load text files
        for register in ["canonical", "headlines"]:
            text_path = TEXT_FILES[newspaper_name][register]
            print(f"  Loading text: {text_path}")
            self.text_data[newspaper_name][register] = read_plain_text(text_path)

        # Load CoNLL-U dependency files
        for register in ["canonical", "headlines"]:
            conllu_path = CONLLU_FILES[newspaper_name][register]
            print(f"  Loading dependencies: {conllu_path}")
            # Convert generator to list
            self.dependency_data[newspaper_name][register] = list(read_conllu(conllu_path))

        # Load constituency files
        for register in ["canonical", "headlines"]:
            const_path = CONST_FILES[newspaper_name][register]
            print(f"  Loading constituency: {const_path}")
            self.constituency_data[newspaper_name][register] = read_constituency(const_path)

        self.loaded_newspapers.append(newspaper_name)
        print(f"  Completed loading {newspaper_name}")

    def get_text_data(self, newspaper: str, register: str) -> List[str]:
        """Get text data for a specific newspaper and register."""
        self._ensure_loaded(newspaper)
        return self.text_data[newspaper][register]

    def get_dependency_data(self, newspaper: str, register: str) -> List[TokenList]:
        """Get dependency parse data for a specific newspaper and register."""
        self._ensure_loaded(newspaper)
        return self.dependency_data[newspaper][register]

    def get_constituency_data(self, newspaper: str, register: str) -> List[Tree]:
        """Get constituency parse data for a specific newspaper and register."""
        self._ensure_loaded(newspaper)
        return self.constituency_data[newspaper][register]

    def get_canonical_text(self, newspaper: str) -> List[str]:
        """Convenience method to get canonical text."""
        return self.get_text_data(newspaper, "canonical")

    def get_headlines_text(self, newspaper: str) -> List[str]:
        """Convenience method to get headlines text."""
        return self.get_text_data(newspaper, "headlines")

    def get_canonical_deps(self, newspaper: str) -> List[TokenList]:
        """Convenience method to get canonical dependencies."""
        return self.get_dependency_data(newspaper, "canonical")

    def get_headlines_deps(self, newspaper: str) -> List[TokenList]:
        """Convenience method to get headlines dependencies."""
        return self.get_dependency_data(newspaper, "headlines")

    def get_canonical_const(self, newspaper: str) -> List[Tree]:
        """Convenience method to get canonical constituency parses."""
        return self.get_constituency_data(newspaper, "canonical")

    def get_headlines_const(self, newspaper: str) -> List[Tree]:
        """Convenience method to get headlines constituency parses."""
        return self.get_constituency_data(newspaper, "headlines")

    def _ensure_loaded(self, newspaper: str):
        """Ensure data for the given newspaper is loaded."""
        if newspaper not in self.loaded_newspapers:
            self.load_newspaper_data(newspaper)

    def get_data_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded data."""
        stats = {}
        for newspaper in self.loaded_newspapers:
            stats[newspaper] = {}
            for register in ["canonical", "headlines"]:
                stats[newspaper][register] = {
                    "text_sentences": len(self.text_data[newspaper][register]),
                    "dependency_sentences": len(self.dependency_data[newspaper][register]),
                    "constituency_sentences": len(self.constituency_data[newspaper][register])
                }
        return stats

    def print_data_stats(self):
        """Print data loading statistics."""
        print("\n=== Data Loading Statistics ===")
        stats = self.get_data_stats()
        for newspaper, registers in stats.items():
            print(f"\n{newspaper}:")
            for register, counts in registers.items():
                print(f"  {register}:")
                print(f"    Text sentences: {counts['text_sentences']}")
                print(f"    Dependency sentences: {counts['dependency_sentences']}")
                print(f"    Constituency sentences: {counts['constituency_sentences']}")


# Global instance for easy access
loaded_data = LoadedData()


# Convenience functions for backward compatibility
def get_canonical_text_list(newspaper: str) -> List[str]:
    """Get canonical text list for a newspaper."""
    return loaded_data.get_canonical_text(newspaper)


def get_headlines_text_list(newspaper: str) -> List[str]:
    """Get headlines text list for a newspaper."""
    return loaded_data.get_headlines_text(newspaper)


def get_canonical_dep_list(newspaper: str) -> List[TokenList]:
    """Get canonical dependency list for a newspaper."""
    return loaded_data.get_canonical_deps(newspaper)


def get_headlines_dep_list(newspaper: str) -> List[TokenList]:
    """Get headlines dependency list for a newspaper."""
    return loaded_data.get_headlines_deps(newspaper)


def get_canonical_const_list(newspaper: str) -> List[Tree]:
    """Get canonical constituency list for a newspaper."""
    return loaded_data.get_canonical_const(newspaper)


def get_headlines_const_list(newspaper: str) -> List[Tree]:
    """Get headlines constituency list for a newspaper."""
    return loaded_data.get_headlines_const(newspaper)


if __name__ == "__main__":
    # Test data loading
    print("Testing data loading...")
    loaded_data.load_all_data()
    loaded_data.print_data_stats()