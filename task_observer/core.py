from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


_ALLOWED = {
    Status.PENDING: {Status.RUNNING, Status.FAILED},
    Status.RUNNING: {Status.DONE, Status.FAILED},
    Status.DONE: set(),
    Status.FAILED: {Status.PENDING},
}


@dataclass
class Task:
    id: int
    name: str
    status: Status = Status.PENDING


@dataclass(frozen=True)
class TaskEvent:
    task: Task
    old: Optional[Status]
    new: Status
    timestamp: float = field(default_factory=time.time)


Listener = Callable[[TaskEvent], None]


class TaskObserver:
    """Registry of tasks; listeners are called on every status change."""

    def __init__(self) -> None:
        self._tasks: Dict[int, Task] = {}
        self._listeners: List[Listener] = []
        self._ids = itertools.count(1)

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        """Register a listener; returns a function that unsubscribes it."""
        self._listeners.append(listener)
        return lambda: self._listeners.remove(listener) if listener in self._listeners else None

    def add(self, name: str) -> Task:
        task = Task(next(self._ids), name)
        self._tasks[task.id] = task
        self._notify(TaskEvent(task, None, task.status))
        return task

    def set_status(self, task_id: int, status: Status) -> Task:
        task = self._tasks[task_id]
        if status not in _ALLOWED[task.status]:
            raise ValueError(f"invalid transition {task.status.value} -> {status.value}")
        old, task.status = task.status, status
        self._notify(TaskEvent(task, old, status))
        return task

    def get(self, task_id: int) -> Task:
        return self._tasks[task_id]

    def by_status(self, status: Status) -> List[Task]:
        return [t for t in self._tasks.values() if t.status == status]

    def _notify(self, event: TaskEvent) -> None:
        for listener in list(self._listeners):
            listener(event)
