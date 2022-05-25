class DBStatistics:
    def __init__(self, users_count: int, albums_count: int, images_count: int,):
        self.users_count = users_count
        self.albums_count = albums_count
        self.images_count = images_count

    def __repr__(self):
        return f"DBStatistics(users_count: {self.users_count}, albums_count: {self.albums_count}, images_count: " \
               f"{self.images_count})"


class UserData:
    def __init__(self, display_name: str, email: str, photo_url: str):
        self.display_name = display_name
        self.email = email
        self.photo_url = photo_url

    def __repr__(self):
        return f"UserData(display_name: {self.display_name}, email: {self.email}, photo_url: {self.photo_url})"
