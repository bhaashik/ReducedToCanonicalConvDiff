# Version 1

# import json
# from pathlib import Path
#
# class FeatureSchema:
#     def __init__(self, schema_path: Path):
#         self.schema_path = schema_path
#         self.schema_data = None
#         self.feature_index = {}
#
#     def load_schema(self):
#         with open(self.schema_path, 'r', encoding='utf-8') as f:
#             self.schema_data = json.load(f)
#         self._index_features()
#
#     def _index_features(self):
#         for feature in self.schema_data.get("features", []):
#             self.feature_index[feature["id"]] = feature
#
#     def get_feature_by_id(self, feature_id):
#         return self.feature_index.get(feature_id)
#
#     def list_features(self):
#         return list(self.feature_index.values())
#
#     def __repr__(self):
#         return f"<FeatureSchema with {len(self.feature_index)} features>"

# Version 2

# import json
# from pathlib import Path
#
# class FeatureSchema:
#     def __init__(self, schema_path: Path):
#         self.schema_path = schema_path
#         self.schema_data = None
#         self.feature_index = {}
#
#     def load_schema(self):
#         with open(self.schema_path, 'r', encoding='utf-8') as f:
#             self.schema_data = json.load(f)
#         self._index_features()
#
#     def _index_features(self):
#         for feature in self.schema_data.get("features", []):
#             self.feature_index[feature["id"]] = feature
#
#     def get_feature_by_id(self, feature_id):
#         return self.feature_index.get(feature_id)
#
#     def list_features(self):
#         return list(self.feature_index.values())
#
#     def __repr__(self):
#         return f"<FeatureSchema with {len(self.feature_index)} features>"

# Version 3

# class FeatureValue:
#     def __init__(self, code, desc):
#         self.code = code
#         self.desc = desc
#
# class Feature:
#     def __init__(self, data):
#         self.id = data["id"]
#         self.name = data.get("name")
#         self.mnemonic = data.get("mnemonic")
#         self.description = data.get("description")
#         self.values = [FeatureValue(v["code"], v.get("desc")) for v in data.get("values", [])]
#
# class FeatureSchema:
#     ...
#     def _index_features(self):
#         for fdata in self.schema_data.get("features", []):
#             self.feature_index[fdata["id"]] = Feature(fdata)
#
#     def get_feature_by_id(self, feature_id) -> Feature:
#         return self.feature_index.get(feature_id)
#
# feat = schema.get_feature_by_id("FV001")
# print(feat.mnemonic)
# for v in feat.values:
#     print(v.code, "-", v.desc)

# Version 4

# import json
# from pathlib import Path
# from typing import List, Optional, Dict, Any
#
# class FeatureValue:
#     """
#     Represents one possible value for a linguistic feature.
#     """
#     def __init__(self, code: str, desc: str, extra: Optional[Dict[str, Any]] = None):
#         self.code = code                 # The code (e.g., '0', '1', '2', etc.)
#         self.desc = desc                 # Human-readable description
#         self.extra = extra or {}         # Any extra metadata from schema JSON
#
#     def __repr__(self):
#         return f"FeatureValue(code={self.code!r}, desc={self.desc!r})"
#
#
# class Feature:
#     """
#     Represents a single feature entry from the schema.
#     """
#     def __init__(self, data: Dict[str, Any]):
#         self.id: str = data.get("id")
#         self.name: str = data.get("name")
#         self.mnemonic: str = data.get("mnemonic")
#         self.description: Optional[str] = data.get("description")
#         self.category: Optional[str] = data.get("category")   # optional metadata
#         self.values: List[FeatureValue] = []
#
#         # Parse value definitions
#         for v in data.get("values", []):
#             code = v.get("code")
#             desc = v.get("desc")
#             extra_fields = {k: v[k] for k in v if k not in ("code", "desc")}
#             self.values.append(FeatureValue(code, desc, extra_fields))
#
#     def get_value_by_code(self, code: str) -> Optional[FeatureValue]:
#         """
#         Return a FeatureValue object given its code.
#         """
#         for v in self.values:
#             if v.code == code:
#                 return v
#         return None
#
#     def list_codes(self) -> List[str]:
#         return [v.code for v in self.values]
#
#     def __repr__(self):
#         return f"Feature(id={self.id!r}, mnemonic={self.mnemonic!r}, values={len(self.values)})"
#
#
# class FeatureSchema:
#     """
#     Loads and provides access to the entire feature ontology schema.
#     """
#     def __init__(self, schema_path: Path):
#         self.schema_path = schema_path
#         self.features: Dict[str, Feature] = {}
#
#     def load_schema(self):
#         with open(self.schema_path, "r", encoding="utf-8") as f:
#             raw_data = json.load(f)
#
#         for fdict in raw_data.get("features", []):
#             feat = Feature(fdict)
#             self.features[feat.id] = feat
#
#     def get_feature_by_id(self, feature_id: str) -> Optional[Feature]:
#         return self.features.get(feature_id)
#
#     def get_feature_by_mnemonic(self, mnemonic: str) -> Optional[Feature]:
#         for feat in self.features.values():
#             if feat.mnemonic == mnemonic:
#                 return feat
#         return None
#
#     def list_all_features(self) -> List[Feature]:
#         return list(self.features.values())
#
#     def __repr__(self):
#         return f"<FeatureSchema: {len(self.features)} features loaded>"
#
# from pathlib import Path
# from schema import FeatureSchema
#
# schema = FeatureSchema(Path("data/diff-ontology-ver-3.0.json"))
# schema.load_schema()
#
# # Number of features
# print(schema)
#
# # Access by ID
# feat = schema.get_feature_by_id("FV001")
# print(feat.id, feat.mnemonic, feat.name, feat.description)
#
# # List its possible values
# for val in feat.values:
#     print(val.code, "-", val.desc)
#
# # Access specific value description
# print(feat.get_value_by_code("1").desc)

# Version 5

import json
from pathlib import Path
from typing import List, Optional, Dict, Any

class FeatureValue:
    """
    Represents one possible value for a linguistic feature.
    """
    def __init__(self, code: str, desc: str, extra: Optional[Dict[str, Any]] = None):
        self.code = code                 # The code (e.g., '0', '1', '2', etc.)
        self.desc = desc                 # Human-readable description
        self.extra = extra or {}         # Any extra metadata from schema JSON

    def __repr__(self):
        return f"FeatureValue(code={self.code!r}, desc={self.desc!r})"


class Feature:
    """
    Represents a single feature entry from the schema.
    """
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id")
        self.name: str = data.get("name")
        self.mnemonic: str = data.get("mnemonic")
        self.description: Optional[str] = data.get("description")
        self.category: Optional[str] = data.get("category")   # optional metadata
        self.values: List[FeatureValue] = []

        # Parse value definitions
        for v in data.get("values", []):
            code = v.get("code")
            desc = v.get("desc")
            extra_fields = {k: v[k] for k in v if k not in ("code", "desc")}
            self.values.append(FeatureValue(code, desc, extra_fields))

    def get_value_by_code(self, code: str) -> Optional[FeatureValue]:
        """
        Return a FeatureValue object given its code.
        """
        for v in self.values:
            if v.code == code:
                return v
        return None

    def list_codes(self) -> List[str]:
        return [v.code for v in self.values]

    def __repr__(self):
        return f"Feature(id={self.id!r}, mnemonic={self.mnemonic!r}, values={len(self.values)})"


class FeatureSchema:
    """
    Loads and provides access to the entire feature ontology schema.
    """
    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        self.features: Dict[str, Feature] = {}

    def load_schema(self):
        with open(self.schema_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        for fdict in raw_data.get("features", []):
            feat = Feature(fdict)
            self.features[feat.id] = feat

    def get_feature_by_id(self, feature_id: str) -> Optional[Feature]:
        return self.features.get(feature_id)

    def get_feature_by_mnemonic(self, mnemonic: str) -> Optional[Feature]:
        for feat in self.features.values():
            if feat.mnemonic == mnemonic:
                return feat
        return None

    def list_all_features(self) -> List[Feature]:
        return list(self.features.values())

    def __repr__(self):
        return f"<FeatureSchema: {len(self.features)} features loaded>"

# Usage:

from pathlib import Path
from schema import FeatureSchema

schema = FeatureSchema(Path("data/diff-ontology-ver-3.0.json"))
schema.load_schema()

# Number of features
print(schema)

# Access by ID
feat = schema.get_feature_by_id("FV001")
print(feat.id, feat.mnemonic, feat.name, feat.description)

# List its possible values
for val in feat.values:
    print(val.code, "-", val.desc)

# Access specific value description
print(feat.get_value_by_code("1").desc)
