from fotogo_networking.endpoints import app
import json
import base64
from PIL import Image
from PIL.ExifTags import TAGS

from fotogo_networking.exceptions import UserNotExistsException


def main():
    # from firebase_access.data_structures import Album
    # from firebase_access.data_structures import DateTimeRange
    # from datetime import datetime
    # app.db.create_album(album=Album(
    #     owner_id='cee69ZaPCtaJiKl1JAuaF8Q3if43',
    #     name='test album',
    #     date_range=DateTimeRange(start=datetime(2022, 3, 1), end=datetime(2022, 3, 31))
    # ))
    # exit()

    app.start()

    # print((31).to_bytes(4, byteorder='big'))

    # with open('IMG_20220319_161322.jpg', 'rb') as f:
    #     encoded = base64.b64encode(f.read())
    # string = encoded.decode('utf-8')
    # # print(string)
    # with open('converted.png', 'wb') as f:
    #     f.write(base64.b64decode(string))

    # msg = json.dumps({
    #     'request_type': 0,  # a number representing the request type id
    #     'args': {
    #         'uid': 'user-id',  # user id (string)
    #         # OPTIONAL
    #         'album_data': dict(owner_id='',
    #                            name='',
    #                            date_range=['yyyy-mm-dd',
    #                                        'yyyy-mm-dd'],
    #                            is_built=False,
    #                            tags=[int],
    #                            location=(0.0, 0.0),
    #                            permitted_users=[str]
    #                            ),
    #         'album_id': 'str',
    #         'images_id': [str]
    #     },
    #     'body': '',  # list of image data (optional)
    # })
    # length = len(msg)
    # print(length)
    # length = length.to_bytes(4, 'big')
    # print(length)
    # msg = length + msg.encode()
    # print(msg)

    # GET IMAGE METADATA
    # img: Image = Image.open('converted.png')
    # exifdata = img.getexif()
    # print(exifdata)
    # for tag_id in exifdata:
    #     # get the tag name, instead of human unreadable tag id
    #     tag = TAGS.get(tag_id, tag_id)
    #     data = exifdata.get(tag_id)
    #     # decode bytes
    #     if isinstance(data, bytes):
    #         data = data.decode()
    #     print(f"{tag:25}: {data}")

    req = b'length', {
        'request_id': 0,
        'id_token': '',
        'args': {
            # OPTIONAL
            'album_data': dict(owner_id='',
                               name='',
                               date_range=['yyyy-mm-dd',
                                           'yyyy-mm-dd'],
                               is_built=False,
                               tags=[int],
                               location=(0.0, 0.0),
                               permitted_users=[str]
                               ),
            'album_id': 'str',
            'images_id': [str]
        },
        'payload': [
            # image list base64 string encoded (optional)
            dict(
                file_name='',
                timestamp=['yyyy-mm-dd',
                           'yyyy-mm-dd'],
                location=(0.0, 0.0),  # optional
                tag=0,
                containing_albums=[],
                data='',
            )
        ],
    }

    res = b'length', {
        'status_code': 200,
        'payload': any,
    }

    """
    Request                                 Arguments                                           Response Args
    ----------------------------------------------------------------------------------------------------------
    auth ?                                                                                      bool
    check user exists                       uid                                                 bool
    create account                          uid                                                 
    delete user data                        uid                                                 
    
    create album                            uid, album object                                   album id
    get album details                       uid(, album id)                                     album object(s)
    get album contents                      uid, album id                                       list of image objects
    update album (title, dates, etc)        uid, album id, album object (data to update)
    add to album                            uid, album id, images list <OPEN IMAGE STREAM>
    remove from album                       uid, album id, image id list
    build album                             uid, album id
    delete album                            uid, album id
    
    upload image (to unbuilt album)         uid, image list <OPEN IMAGE STREAM>
    delete image ?                          uid, image id list
    
                                                                                                --------------
                                                                        if any errors, put the error message in the body
    """


if __name__ == '__main__':
    main()
