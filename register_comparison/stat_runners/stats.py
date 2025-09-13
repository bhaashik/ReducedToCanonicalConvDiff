
# Version 1

# import math
# from typing import Dict, Tuple, Any
# import pandas as pd
# from scipy.stats import chi2_contingency, fisher_exact
#
# class StatsRunner:
#     """
#     Runs statistical tests (Chi-square, Fisher's exact) and computes odds ratios
#     for feature frequency counts.
#     """
#
#     def __init__(self, min_expected_count: int = 5):
#         self.min_expected_count = min_expected_count
#
#     def _make_contingency(self, count_a: int, total_a: int,
#                           count_b: int, total_b: int) -> Tuple[list, bool]:
#         """
#         Build a 2x2 contingency table and check if Fisher is more appropriate.
#         """
#         contingency = [
#             [count_a, total_a - count_a],
#             [count_b, total_b - count_b]
#         ]
#         # Expected counts check (for Chi-square validity)
#         expected_ok = all(val >= self.min_expected_count for row in contingency for val in row)
#         return contingency, expected_ok
#
#     def run_tests_for_feature(self,
#                               feature_id: str,
#                               count_a: int, total_a: int,
#                               count_b: int, total_b: int) -> Dict[str, Any]:
#         """
#         Run statistical tests for a single feature comparing two groups.
#         Groups could be: canonical vs headline counts, or newspaper vs others.
#         """
#         contingency, expected_ok = self._make_contingency(count_a, total_a, count_b, total_b)
#
#         chi2, chi_p, odds_ratio, fisher_p = None, None, None, None
#
#         if expected_ok:
#             chi2, chi_p, _, _ = chi2_contingency(contingency)
#         else:
#             odds_ratio, fisher_p = fisher_exact(contingency)
#
#         # Compute odds ratio for reference (if counts are valid)
#         if odds_ratio is None:
#             odds_ratio = self._odds_ratio(contingency)
#
#         return {
#             "feature_id": feature_id,
#             "count_a": count_a,
#             "total_a": total_a,
#             "count_b": count_b,
#             "total_b": total_b,
#             "chi2": chi2,
#             "chi_p": chi_p,
#             "fisher_p": fisher_p,
#             "odds_ratio": odds_ratio
#         }
#
#     def _odds_ratio(self, table_2x2: list) -> float:
#         """
#         Compute odds ratio from a 2x2 contingency table.
#         """
#         a, b = table_2x2[0]
#         c, d = table_2x2[1]
#         # Avoid division by zero
#         if b == 0 or c == 0:
#             return math.inf
#         return (a * d) / (b * c)
#
#     def run_for_dataframe(self, df: pd.DataFrame,
#                           group_a_label: str,
#                           group_b_label: str) -> pd.DataFrame:
#         """
#         Run statistical tests for each feature in a DataFrame with
#         feature counts for two groups.
#         DataFrame columns: feature_id, count_a, total_a, count_b, total_b
#         """
#         results = []
#         for _, row in df.iterrows():
#             res = self.run_tests_for_feature(
#                 feature_id=row["feature_id"],
#                 count_a=row["count_a"],
#                 total_a=row["total_a"],
#                 count_b=row["count_b"],
#                 total_b=row["total_b"]
#             )
#             results.append(res)
#         return pd.DataFrame(results)
#
# # Usage:
#
# from stats import StatsRunner
# import pandas as pd
#
# # Suppose we have feature counts:
# data = [
#     {"feature_id": "FV001", "count_a": 15, "total_a": 100, "count_b": 5, "total_b": 100},
#     {"feature_id": "FV002", "count_a": 40, "total_a": 100, "count_b": 60, "total_b": 100},
# ]
#
# df = pd.DataFrame(data)
#
# stats_runner = StatsRunner()
# results_df = stats_runner.run_for_dataframe(df, "canonical", "headlines")
#
# print(results_df)

# Version 2

import math
from typing import Dict, Tuple, Any
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact

class StatsRunner:
    """
    Runs statistical tests (Chi-square, Fisher's exact) and computes odds ratios
    for feature frequency counts.
    """

    def __init__(self, min_expected_count: int = 5):
        self.min_expected_count = min_expected_count

    def _make_contingency(self, count_a: int, total_a: int,
                          count_b: int, total_b: int) -> Tuple[list, bool]:
        """
        Build a 2x2 contingency table and check if Fisher is more appropriate.
        """
        contingency = [
            [count_a, total_a - count_a],
            [count_b, total_b - count_b]
        ]
        # Expected counts check (for Chi-square validity)
        expected_ok = all(val >= self.min_expected_count for row in contingency for val in row)
        return contingency, expected_ok

    def run_tests_for_feature(self,
                              feature_id: str,
                              count_a: int, total_a: int,
                              count_b: int, total_b: int) -> Dict[str, Any]:
        """
        Run statistical tests for a single feature comparing two groups.
        Groups could be: canonical vs headline counts, or newspaper vs others.
        """
        contingency, expected_ok = self._make_contingency(count_a, total_a, count_b, total_b)

        chi2, chi_p, odds_ratio, fisher_p = None, None, None, None

        if expected_ok:
            chi2, chi_p, _, _ = chi2_contingency(contingency)
        else:
            odds_ratio, fisher_p = fisher_exact(contingency)

        # Compute odds ratio for reference (if counts are valid)
        if odds_ratio is None:
            odds_ratio = self._odds_ratio(contingency)

        return {
            "feature_id": feature_id,
            "count_a": count_a,
            "total_a": total_a,
            "count_b": count_b,
            "total_b": total_b,
            "chi2": chi2,
            "chi_p": chi_p,
            "fisher_p": fisher_p,
            "odds_ratio": odds_ratio
        }

    def _odds_ratio(self, table_2x2: list) -> float:
        """
        Compute odds ratio from a 2x2 contingency table.
        """
        a, b = table_2x2[0]
        c, d = table_2x2[1]
        # Avoid division by zero
        if b == 0 or c == 0:
            return math.inf
        return (a * d) / (b * c)

    def run_for_dataframe(self, df: pd.DataFrame,
                          group_a_label: str,
                          group_b_label: str) -> pd.DataFrame:
        """
        Run statistical tests for each feature in a DataFrame with
        feature counts for two groups.
        DataFrame columns: feature_id, count_a, total_a, count_b, total_b
        """
        results = []
        for _, row in df.iterrows():
            res = self.run_tests_for_feature(
                feature_id=row["feature_id"],
                count_a=row["count_a"],
                total_a=row["total_a"],
                count_b=row["count_b"],
                total_b=row["total_b"]
            )
            results.append(res)
        return pd.DataFrame(results)

# # Usage:
#
# #from stats import StatsRunner
# import pandas as pd
#
# # Suppose we have feature counts:
# data = [
#     {"feature_id": "FV001", "count_a": 15, "total_a": 100, "count_b": 5, "total_b": 100},
#     {"feature_id": "FV002", "count_a": 40, "total_a": 100, "count_b": 60, "total_b": 100},
# ]
#
# df = pd.DataFrame(data)
#
# stats_runner = StatsRunner()
# results_df = stats_runner.run_for_dataframe(df, "canonical", "headlines")
#
# print(results_df)
