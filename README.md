# task-observer

Minimal observer-pattern task tracker. Subscribe a callback and get a `TaskEvent`
whenever a task is added or changes status (`pending -> running -> done/failed`).

```python
from task_observer import TaskObserver, Status
obs = TaskObserver()
obs.subscribe(lambda e: print(e.task.name, e.old, "->", e.new))
t = obs.add("build"); obs.set_status(t.id, Status.RUNNING)
```

Run tests: `pytest`
