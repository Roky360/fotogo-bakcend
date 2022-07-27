class DBStatistics:
    """
    Holds statistics about the system.

    * Right now contains how many users, albums and images are stored in the DB.
    """

    def __init__(self, users_count: int, albums_count: int, images_count: int, ):
        self.users_count = users_count
        self.albums_count = albums_count
        self.images_count = images_count

    def __repr__(self):
        return f"DBStatistics(users_count: {self.users_count}, albums_count: {self.albums_count}, images_count: " \
               f"{self.images_count})"


class UserData:
    """
    Holds a user's data.

    Contains user's full name, email and a URL to its profile photo.
    """

    def __init__(self, uid: str, display_name: str, email: str, photo_url: str, privilege_level: int):
        self.uid = uid
        self.display_name = display_name
        self.email = email
        self.photo_url = photo_url
        self.privilege_level = privilege_level

    def __repr__(self):
        return f"UserData(uid: {self.uid} ,display_name: {self.display_name}, email: {self.email}, " \
               f"photo_url: {self.photo_url}, privilege_level: {self.privilege_level})"
