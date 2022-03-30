from enum import Enum


class Caller(Enum):
    Server = 0
    Client = 1


def prompt_log(caller: Caller, msg):
    def decorator(func):
        def print_log_message(*args, **kwargs):
            rv = func(*args, **kwargs)
            print(f"[{caller.name}] {msg}")
            return rv

        return print_log_message

    return decorator
