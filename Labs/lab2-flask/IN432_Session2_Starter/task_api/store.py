class TaskStore:
    """Per-app teaching store. Data lasts only for this process instance."""

    def __init__(self):
        self._items = {
            1: {"id": 1, "title": "Prepare lab", "done": False},
            2: {"id": 2, "title": "Review REST notes", "done": True},
            3: {"id": 3, "title": "Test Flask routes", "done": False},
        }
        self._next_id = 4

    def list(self):
        return [item.copy() for item in self._items.values()]

    def get(self, task_id):
        item = self._items.get(task_id)
        return item.copy() if item is not None else None

    def create(self, fields):
        task_id = self._next_id
        self._next_id += 1
        item = {"id": task_id, "title": fields["title"],
                "done": fields.get("done", False)}
        self._items[task_id] = item
        return item.copy()

    def update(self, task_id, fields):
        item = self._items[task_id].copy()
        item.update(fields)
        self._items[task_id] = item
        return item.copy()

    def delete(self, task_id):
        return self._items.pop(task_id, None) is not None
