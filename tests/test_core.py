import pytest

from task_observer import Status, TaskObserver


def test_listener_receives_events():
    obs, events = TaskObserver(), []
    obs.subscribe(events.append)
    t = obs.add("build")
    obs.set_status(t.id, Status.RUNNING)
    obs.set_status(t.id, Status.DONE)
    assert [(e.old, e.new) for e in events] == [
        (None, Status.PENDING),
        (Status.PENDING, Status.RUNNING),
        (Status.RUNNING, Status.DONE),
    ]


def test_invalid_transition():
    obs = TaskObserver()
    t = obs.add("x")
    with pytest.raises(ValueError):
        obs.set_status(t.id, Status.DONE)


def test_unsubscribe_and_query():
    obs, events = TaskObserver(), []
    unsub = obs.subscribe(events.append)
    unsub()
    t = obs.add("x")
    assert events == []
    assert obs.by_status(Status.PENDING) == [t]
