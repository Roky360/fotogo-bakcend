from enum import IntEnum


class RequestType(IntEnum):
    # Users
    UserAuth = 0,
    CheckUserExists = 1,
    CreateAccount = 2,
    DeleteAccount = 3,
    # Albums
    CreateAlbum = 4,
    GetAlbumDetails = 5,
    GetAlbumContents = 6,
    UpdateAlbum = 7,
    AddToAlbum = 8,
    RemoveFromAlbum = 9,
    DeleteAlbum = 10,
    # Photos
    UploadImage = 11,
    DeleteImage = 12,
