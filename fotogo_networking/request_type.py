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
    BuildAlbum = 10,
    DeleteAlbum = 11,
    # Photos
    UploadImage = 12,
    DeleteImage = 13,
