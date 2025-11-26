"""Build panel graphs from control instances."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from cv_pipeline.control_classifier import ControlInstance


@dataclass(slots=True)
class ControlNode:
    instance: ControlInstance
    center_x: float
    center_y: float
    width: int
    height: int
    row: int = -1
    column: int = -1


@dataclass
class PanelGraph:
    nodes: list[ControlNode] = field(default_factory=list)

    @classmethod
    def from_instances(cls, instances: Iterable[ControlInstance]) -> PanelGraph:
        nodes = []
        for instance in instances:
            x, y, w, h = instance.bbox
            nodes.append(
                ControlNode(
                    instance=instance,
                    center_x=x + w / 2,
                    center_y=y + h / 2,
                    width=w,
                    height=h,
                )
            )
        graph = cls(nodes=nodes)
        graph._assign_rows()
        graph._assign_columns()
        return graph

    def rows(self) -> list[list[ControlNode]]:
        return _group_by_index(self.nodes, attr="row")

    def columns(self) -> list[list[ControlNode]]:
        return _group_by_index(self.nodes, attr="column")

    def _assign_rows(self) -> None:
        for idx, group in enumerate(_cluster(self.nodes, key=lambda n: n.center_y, threshold=15.0)):
            for node in group:
                node.row = idx

    def _assign_columns(self) -> None:
        for idx, group in enumerate(_cluster(self.nodes, key=lambda n: n.center_x)):
            for node in group:
                node.column = idx


def _cluster(
    nodes: list[ControlNode], key: Callable[[ControlNode], float], threshold: float = 30.0
) -> list[list[ControlNode]]:
    sorted_nodes = sorted(nodes, key=key)
    groups: list[list[ControlNode]] = []
    current: list[ControlNode] = []
    last_value: float | None = None
    for node in sorted_nodes:
        value = key(node)
        if last_value is None or abs(value - last_value) <= threshold:
            current.append(node)
        else:
            groups.append(current)
            current = [node]
        last_value = value
    if current:
        groups.append(current)
    return groups


def _group_by_index(nodes: list[ControlNode], attr: str) -> list[list[ControlNode]]:
    groups: dict[int, list[ControlNode]] = {}
    for node in nodes:
        index = getattr(node, attr)
        if index < 0:
            continue
        groups.setdefault(index, []).append(node)
    return [groups[i] for i in sorted(groups)]
