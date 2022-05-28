class UserNotAuthenticatedException(Exception):
    """An exception that indicates that a user's id token is invalid."""
    def __init__(self, message=None):
        self._message = message

    def __str__(self):
        return self._message if self._message is not None else \
            "Invalid id token."


class UserNotExistsException(Exception):
    """An exception that indicates that a user does not exist."""
    def __init__(self, message=None):
        self._message = message

    def __str__(self):
        return self._message if self._message is not None else \
            "User does not exists."


class AlbumNotExistsException(Exception):
    """An exception that indicates that an album does not exist."""
    def __init__(self, message=None):
        self._message = message

    def __str__(self):
        return self._message if self._message is not None else \
            "Album does not exists."


class ImageNotExistsException(Exception):
    """An exception that indicates that an image does not exist."""
    def __init__(self, message=None):
        self._message = message

    def __str__(self):
        return self._message if self._message is not None else \
            "Image does not exists."


class PermissionDeniedException(Exception):
    """An exception that indicates that a client does not have the right permission to access a resource."""
    def __init__(self, message=None):
        self._message = message

    def __str__(self):
        return self._message if self._message is not None else \
            "Does not have the right permission to that source."
