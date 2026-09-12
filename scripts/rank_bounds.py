"""Float32 rank contributions and the independent array certificate."""
from __future__ import annotations
import csv, math, uuid
from dataclasses import dataclass
from pathlib import Path
import numpy as np
RRF_K = 60
REPORT_CAP = 100
def position_score(rank_one_based: np.ndarray | int) -> np.ndarray | np.float32:
    rank = np.asarray(rank_one_based, dtype=np.float32)
    return np.float32(np.float32(1.0) / (rank + np.float32(RRF_K - 1)))


def tie_key(point_id: str) -> int:
    return uuid.UUID(point_id).int


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            output.setdefault(str(row["query_id"]), {})[str(row["doc_id"])] = int(
                row["relevance"]
            )
    return output


@dataclass(frozen=True)
class Frontier:
    output: tuple[str, ...]
    certified_k: int
    at_least_cap: bool
    next_candidate: int | None
    blocker: int | None
    anonymous_blocks: bool
    next_gap: float
    seen_count: int
    seen_first: np.ndarray
    seen_second: np.ndarray
    lower: np.ndarray
    upper: np.ndarray


class UnequalDepthCertificate:
    """NRA-style exact ordered-prefix certificate for two unequal depths."""

    def __init__(
        self,
        first: list[str],
        second: list[str],
        report_cap: int = REPORT_CAP,
        first_exhausted: bool = False,
        second_exhausted: bool = False,
    ) -> None:
        if not first:
            raise ValueError("first ranked stream must be non-empty")
        if len(set(first)) != len(first) or len(set(second)) != len(second):
            raise ValueError("duplicate identity within a channel prefix")
        self.first = first
        self.second = second
        self.first_max = len(first)
        self.second_max = len(second)
        self.first_exhausted = first_exhausted
        self.second_exhausted = second_exhausted
        self.report_cap = report_cap
        identities = list(dict.fromkeys(self.first + self.second))
        self.identities = np.asarray(identities, dtype=object)
        index = {point_id: offset for offset, point_id in enumerate(identities)}
        self.first_rank = np.full(len(identities), self.first_max + 1, dtype=np.int32)
        self.second_rank = np.full(len(identities), self.second_max + 1, dtype=np.int32)
        for rank, point_id in enumerate(self.first, 1):
            self.first_rank[index[point_id]] = rank
        for rank, point_id in enumerate(self.second, 1):
            self.second_rank[index[point_id]] = rank
        self.tie_keys = [tie_key(point_id) for point_id in identities]

    def _top(self, values: np.ndarray, eligible: np.ndarray, count: int) -> list[int]:
        indexes = np.flatnonzero(eligible)
        if not len(indexes) or count <= 0:
            return []
        if len(indexes) > count:
            local = values[indexes]
            selected = np.argpartition(local, -count)[-count:]
            threshold = float(local[selected].min())
            indexes = indexes[local >= threshold]
        return sorted(
            (int(value) for value in indexes),
            key=lambda value: (-float(values[value]), self.tie_keys[value]),
        )[:count]

    def frontier(self, first_depth: int, second_depth: int) -> Frontier:
        if not 0 <= first_depth <= self.first_max or not 0 <= second_depth <= self.second_max:
            raise ValueError("depth outside available prefix")
        seen_first = self.first_rank <= first_depth
        seen_second = self.second_rank <= second_depth
        seen = seen_first | seen_second
        lower = np.zeros(len(self.identities), dtype=np.float32)
        if np.any(seen_first):
            lower[seen_first] = np.float32(
                lower[seen_first] + position_score(self.first_rank[seen_first])
            )
        if np.any(seen_second):
            lower[seen_second] = np.float32(
                lower[seen_second] + position_score(self.second_rank[seen_second])
            )
        next_first = float(position_score(first_depth + 1))
        if first_depth == self.first_max and self.first_exhausted:
            next_first = 0.0
        next_second = float(position_score(second_depth + 1))
        if second_depth == self.second_max and self.second_exhausted:
            next_second = 0.0
        anonymous_upper = float(np.float32(next_first + next_second))
        upper = lower.copy()
        upper[seen & ~seen_first] = np.float32(upper[seen & ~seen_first] + next_first)
        upper[seen & ~seen_second] = np.float32(upper[seen & ~seen_second] + next_second)

        lower_order = self._top(lower, seen, self.report_cap)
        upper_order = self._top(upper, seen, self.report_cap + 1)
        fixed: set[int] = set()
        next_candidate: int | None = None
        blocker: int | None = None
        anonymous_blocks = False
        next_gap = -math.inf
        for candidate in lower_order:
            competitors = [
                value for value in upper_order if value not in fixed and value != candidate
            ]
            competitor = competitors[0] if competitors else None
            competitor_upper = float(upper[competitor]) if competitor is not None else -math.inf
            threshold = max(anonymous_upper, competitor_upper)
            gap = float(lower[candidate]) - threshold
            fails = float(lower[candidate]) <= anonymous_upper
            if not fails and competitor is not None:
                fails = float(lower[candidate]) < competitor_upper or (
                    float(lower[candidate]) == competitor_upper
                    and self.tie_keys[candidate] > self.tie_keys[competitor]
                )
            if fails:
                next_candidate = candidate
                blocker = competitor if competitor_upper >= anonymous_upper else None
                anonymous_blocks = anonymous_upper >= competitor_upper
                next_gap = gap
                break
            fixed.add(candidate)

        output = tuple(str(self.identities[value]) for value in lower_order[: len(fixed)])
        return Frontier(
            output=output,
            certified_k=len(fixed),
            at_least_cap=len(fixed) == self.report_cap,
            next_candidate=next_candidate,
            blocker=blocker,
            anonymous_blocks=anonymous_blocks,
            next_gap=next_gap,
            seen_count=int(seen.sum()),
            seen_first=seen_first,
            seen_second=seen_second,
            lower=lower,
            upper=upper,
        )





DATASETS=('msmarco-passage-trec-dl-2019','msmarco-passage-trec-dl-2020','nfcorpus','scifact','trec-covid')
