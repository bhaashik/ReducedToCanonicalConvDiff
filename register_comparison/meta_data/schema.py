import json
from pathlib import Path
from typing import List, Optional, Dict, Any


class FeatureValue:
    """
    Represents one possible value for a linguistic feature.
    """

    def __init__(self, value: str, mnemonic: Optional[str] = None):
        self.value = value  # The actual value (e.g., 'article deletion')
        self.mnemonic = mnemonic  # Mnemonic code (e.g., 'ART-DEL')

    def __repr__(self):
        return f"FeatureValue(value={self.value!r}, mnemonic={self.mnemonic!r})"


class Feature:
    """
    Represents a single feature entry from the schema.
    """

    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get("name")
        self.mnemonic_code: str = data.get("mnemonic_code")
        self.group: str = data.get("group")
        self.description: str = data.get("description", "")
        self.category: str = data.get("category")
        self.parse_types: List[str] = data.get("parse_types", [])
        self.extra: List[str] = data.get("extra", [])

        # Parse values and their mnemonics
        self.values: List[FeatureValue] = []
        values = data.get("values", [])
        value_mnemonics = data.get("value_mnemonics", {})

        for value in values:
            mnemonic = value_mnemonics.get(value)
            self.values.append(FeatureValue(value, mnemonic))

    def get_value_by_name(self, value_name: str) -> Optional[FeatureValue]:
        """
        Return a FeatureValue object given its name.
        """
        for v in self.values:
            if v.value == value_name:
                return v
        return None

    def get_value_by_mnemonic(self, mnemonic: str) -> Optional[FeatureValue]:
        """
        Return a FeatureValue object given its mnemonic code.
        """
        for v in self.values:
            if v.mnemonic == mnemonic:
                return v
        return None

    def list_value_names(self) -> List[str]:
        """Return list of all value names."""
        return [v.value for v in self.values]

    def list_value_mnemonics(self) -> List[str]:
        """Return list of all value mnemonics."""
        return [v.mnemonic for v in self.values if v.mnemonic]

    def __repr__(self):
        return f"Feature(name={self.name!r}, mnemonic_code={self.mnemonic_code!r}, values={len(self.values)})"


class FeatureSchema:
    """
    Loads and provides access to the entire feature ontology schema.
    """

    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        self.features: Dict[str, Feature] = {}  # keyed by mnemonic_code
        self.features_by_name: Dict[str, Feature] = {}  # keyed by name

    def load_schema(self):
        """Load the schema from JSON file."""
        with open(self.schema_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Access the diff-schema section
        diff_schema = raw_data.get("diff-schema", {})
        features_data = diff_schema.get("features", [])

        # Clear existing features
        self.features.clear()
        self.features_by_name.clear()

        # Load each feature
        for feature_data in features_data:
            feature = Feature(feature_data)

            # Index by mnemonic code (primary key)
            if feature.mnemonic_code:
                self.features[feature.mnemonic_code] = feature

            # Also index by name for convenience
            if feature.name:
                self.features_by_name[feature.name] = feature

    def get_feature_by_mnemonic(self, mnemonic_code: str) -> Optional[Feature]:
        """Get feature by its mnemonic code (e.g., 'FW-DEL')."""
        return self.features.get(mnemonic_code)

    def get_feature_by_name(self, name: str) -> Optional[Feature]:
        """Get feature by its name (e.g., 'Function Word Deletion')."""
        return self.features_by_name.get(name)

    def list_all_features(self) -> List[Feature]:
        """Return all loaded features."""
        return list(self.features.values())

    def list_features_by_category(self, category: str) -> List[Feature]:
        """Return all features in a specific category."""
        return [f for f in self.features.values() if f.category == category]

    def list_features_by_group(self, group: str) -> List[Feature]:
        """Return all features in a specific group."""
        return [f for f in self.features.values() if f.group == group]

    def list_categories(self) -> List[str]:
        """Return all unique categories."""
        return list(set(f.category for f in self.features.values() if f.category))

    def list_groups(self) -> List[str]:
        """Return all unique groups."""
        return list(set(f.group for f in self.features.values() if f.group))

    def __repr__(self):
        return f"<FeatureSchema: {len(self.features)} features loaded>"


# Example usage:
if __name__ == "__main__":
    # Uncomment and modify path as needed
    # schema = FeatureSchema(Path("schema.json"))
    # schema.load_schema()
    #
    # # Number of features
    # print(schema)
    #
    # # Access by mnemonic code
    # feat = schema.get_feature_by_mnemonic("FW-DEL")
    # if feat:
    #     print(f"Feature: {feat.name}")
    #     print(f"Description: {feat.description}")
    #     print(f"Category: {feat.category}")
    #     print(f"Parse types: {feat.parse_types}")
    #     print("Values:")
    #     for val in feat.values:
    #         print(f"  {val.value} -> {val.mnemonic}")
    #
    # # List all lexical features
    # lexical_features = schema.list_features_by_category("lexical")
    # print(f"\nFound {len(lexical_features)} lexical features")
    #
    # # Get specific value information
    # if feat:
    #     article_del = feat.get_value_by_name("article deletion")
    #     if article_del:
    #         print(f"\nArticle deletion mnemonic: {article_del.mnemonic}")
    pass