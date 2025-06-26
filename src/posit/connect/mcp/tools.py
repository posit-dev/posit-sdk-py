from ..client import Client
from ..resources import Resource


def current_user():
    """Fetches the current user."""
    client = Client()
    return client.me


def get_content_for_user(user_id: str):
    """Fetches content for a specific user by their user guid."""
    client = Client()
    return client.content.find(owner_guid=user_id)


TOOLS = [
    current_user,
    get_content_for_user,
]


def register_service_method(method_func):
    """A decorator that registers a class method and returns a wrapper.

    The wrapper ensures 'self.ctx' exists before calling the original method.
    """
    print(f"Registering method: {method_func.__name__}")

    # Store the unbound function (the method itself)
    TOOLS.append(method_func)

    # This is the actual decorator return. It's a wrapper function that will
    # replace the original method in the class.
    def wrapper(self: Resource, *args, **kwargs):
        # 'self' is available here because this 'wrapper' will be called
        # as a method on an instance of the class (e.g., my_service_instance.do_something()).

        # Optional: Check if ctx is initialized. If the method relies on it,
        # this provides an early, clear error.
        if not hasattr(self, "_ctx") or self._ctx is None:
            raise AttributeError(
                f"Method '{method_func.__name__}' requires 'self.ctx' to be initialized on the instance "
                f"(for service '{getattr(self, 'service_id', 'unknown')}' of type {type(self).__name__})."
            )

        print(f"  Calling wrapped method '{method_func.__name__}'")
        # Call the original method. Since it uses `self.ctx` internally,
        # we just pass `self` and any other arguments.
        return method_func(self, *args, **kwargs)

    return wrapper
