from typing import Callable, Any


class Serializer:
    def __init__(self, callback: Callable[[Any], bytes]) -> None:
        self.callback = callback

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.callback(*args, **kwargs)
