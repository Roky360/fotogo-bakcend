from datetime import datetime

from google.cloud.firestore_v1 import GeoPoint


class DateTimeRange:
    """
    Holds a pair of datetime objects representing a range of dates.
    """

    def __init__(self, start: datetime, end: datetime):
        self.start = start
        self.end = end

    def format(self):
        return [
            f"{str(self.start.year).zfill(4)}-{str(self.start.month).zfill(2)}-{str(self.start.day).zfill(2)}",
            f"{str(self.end.year).zfill(4)}-{str(self.end.month).zfill(2)}-{str(self.end.day).zfill(2)}"
        ]

    def __str__(self):
        return [
            f"{str(self.start.year).zfill(4)}-{str(self.start.month).zfill(2)}-{str(self.start.day).zfill(2)}",
            f"{str(self.end.year).zfill(4)}-{str(self.end.month).zfill(2)}-{str(self.end.day).zfill(2)}"
        ].__str__()

    def __repr__(self):
        return f"DateTimeRange(start: {str(self.start.year).zfill(4)}-{str(self.start.month).zfill(2)}-{str(self.start.day).zfill(2)}, " \
               f"end: {str(self.end.year).zfill(4)}-{str(self.end.month).zfill(2)}-{str(self.end.day).zfill(2)})"


class AlbumDetails:
    """
    Holds the required data for an album, as stored in the DB.
    """

    def __init__(self, owner_id: str, album_id: str, name: str, date_range: DateTimeRange, last_modified: datetime,
                 is_built: bool = False, tags: list[int] = None, permitted_users: list[str] = None,
                 cover_image: str = None):
        if permitted_users is None:
            permitted_users = []
        if tags is None:
            tags = []
        self.owner_id = owner_id
        self.id = album_id
        self.name = name
        self.date_range = date_range
        self.last_modified = last_modified
        self.is_built = is_built
        self.tags = tags
        self.permitted_users = permitted_users
        self.cover_image = cover_image

    def __repr__(self):
        return f"Album(owner_id: {self.owner_id}, id: {self.id}, name: {self.name}, date_range: {self.date_range}, " \
               f"last_modified: {self.last_modified}, is_built: {self.is_built}, tags: {self.tags}, " \
               f"permitted_users: {self.permitted_users})"


class Image:
    """
    Holds the required data for an image, as stored in the DB.
    """
    def __init__(self, owner_id: str, file_name: str, timestamp: datetime, image_url: str = None, tag: int = None,
                 location: GeoPoint = None, containing_albums: list[str] = None):
        if containing_albums is None:
            containing_albums = []
        self.owner_id = owner_id
        self.file_name = file_name
        self.timestamp = timestamp
        self.url = image_url
        self.location = location
        self.tag = tag
        self.containing_albums = containing_albums

    def __repr__(self):
        return f"Image(owner_id: {self.owner_id}, file_name: {self.file_name}, timestamp: {self.timestamp}, " \
               f"url: {self.url}, location: {self.location}, tag: {self.tag}, " \
               f"containing_albums: {self.containing_albums})"
