# Python guide for this lab

Python uses indentation instead of braces to delimit a class, method, branch or
loop. A colon introduces a block. Keep the supplied indentation and method names.

    class Counter:
        def describe(self, number):
            if number is None:
                return "No number"
            return str(number)

`def` declares a function or method. `self` is the receiving instance, like Java
`this`. `class Child(Parent)` declares inheritance, like `extends Parent` in Java.
The import `from .extensions import db` means import db from the same package.

A dictionary maps keys to values. `data["name"]` reads a required key;
`data.get("count", 0)` reads it or uses a default when the key is missing.

    data = {"name": "Mira", "active": False}
    if "active" in data:
        print(data["active"])

The print executes even though the stored value is False. `if data.get("active")`
would test truthiness instead. Do not use that truthiness test for partial updates.

A list stores ordered items. `append` adds an item; `remove` removes a known item.

    names = []
    for person in [{"name": "Mira"}, {"name": "Omar"}]:
        names.append(person["name"])

`x is None` checks absence. `x == y` compares values. `x in collection` tests
membership. Python is case-sensitive. In Python use True, False and None. In JSON
payload files use true, false and null. JSON property names use double quotes.

`with app.app_context():` activates the app for the indented database work.
`try` / `except` handles errors; `raise` reports an exception. The supplied commit
helper rolls back a database transaction after a SQLAlchemy error.

The lab's _commit and require helpers are application functions. db.session,
db.Column and db.relationship come from the database extension or SQLAlchemy.
