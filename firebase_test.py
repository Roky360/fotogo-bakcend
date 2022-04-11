from datetime import datetime

import firebase_admin
import google.cloud.firestore_v1.client
from firebase_admin import credentials, firestore, storage, auth
from firebase_admin.auth import UserRecord

from db_services.data_structures import AlbumDetails, DateTimeRange, Image
from db_services.db_service import DBService


def main():
    # initialize
    cred = credentials.Certificate("fotogo-5e99f-firebase-adminsdk-1ogpp-c9e66a13ab.json")
    app: firebase_admin.App = firebase_admin.initialize_app(cred)
    # app: firebase_admin.App = firebase_admin.initialize_app(cred, {
    #     'storageBucket': 'fotogo-5e99f.appspot.com'
    # })



    t = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIwNmExMTkxNThlOGIyODIxNzE0MThhNjdkZWE4Mzc0MGI1ZWU3N2UiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiRWRlbiBTaGFrZWQiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EtL0FPaDE0R2c0QkZmMnRVbElIcUloTGJxeGM5Zm55cVZBMW9GSFNfY19QbmEzRXNJPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2ZvdG9nby01ZTk5ZiIsImF1ZCI6ImZvdG9nby01ZTk5ZiIsImF1dGhfdGltZSI6MTY0ODEzMDQ2MSwidXNlcl9pZCI6ImNlZTY5WmFQQ3RhSmlLbDFKQXVhRjhRM2lmNDMiLCJzdWIiOiJjZWU2OVphUEN0YUppS2wxSkF1YUY4UTNpZjQzIiwiaWF0IjoxNjQ4MTMwNDYxLCJleHAiOjE2NDgxMzQwNjEsImVtYWlsIjoiZWRlbnNoa2RAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMDE5MjI1Nzk1NTA1NzU5MTgyMDYiXSwiZW1haWwiOlsiZWRlbnNoa2RAZ21haWwuY29tIl19LCJzaWduX2luX3Byb3ZpZGVyIjoiZ29vZ2xlLmNvbSJ9fQ.Yhqx8B_7_umNvHejTOQ9jxVtHoDnIwTBF3ZvdAvGCOgWFIiNB5kMtFAtzdZW8RFElg0kImWjlWxcUy0LMRQcN7XZKl75LihSMQWma1B9zwwh0oPoe_OWx3Eb0JDXe4sn4DPZGxZlKKbtBJDpK9_xtqbDd6W6aaugiR_4OGT9T6LbnHyCmXqDKvqELyAazXeDlrHavqJG3r0gaHDNGyPOpKA4js3iFVL-8QBLFMmmSPGj_2sGz_LA4siJ8X_OMd2FcQY4PQclMLZPHAtTkldOfQq0n5gC8Ob-ex4re5LbJTg98XY6npjBmwXSCdMrJ0brY9Xlwcc8Dn2ZeyL6OF0bFw"
    res = auth.verify_id_token(t)
    print(res)
    print(res['uid'])

    exit()



    # db: google.cloud.firestore_v1.client.Client = firestore.client()

    # add documents with auto IDs
    # data = {'name': 'Shoompy Shmoopy', 'age': 40, 'signed in': False}
    # db.collection('people').add({'name': 'Shoompy Shmoopy', 'age': 40, 'signed in': False})

    # Set document with known IDs
    # db.collection('persons').document('edenshaked').collection('albums').add({'name': 'Amsterdam'})

    uid = 'cee69ZaPCtaJiKl1JAuaF8Q3if43'  # Eden Shaked
    tkn = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjcyOTE4OTQ1MGQ0OTAyODU3MDQyNTI2NmYwM2U3MzdmNDVhZjI5MzIiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI4OTg4ODE4ODYwMjctcWRmcmp1ZWNic2c5MHZkYmo0bHN0cTBhZ2RmcWwydWouYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI4OTg4ODE4ODYwMjctdGtpaWlyOHYwb2liam1ia2RmNTBuYmF2MG5vZm43aDEuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDY3NTc3NjcxNDAzMjIwMjgwODAiLCJoZCI6ImtzaGFwaXJhLm9ydC5vcmcuaWwiLCJlbWFpbCI6InN0MzgyNzg3M0Brc2hhcGlyYS5vcnQub3JnLmlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiLXoteT158g16nXp9eTIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FBVFhBSndIZ1hDNnBhdUtfVFlXZnA1cnNHYV9YTE5IWTY0aUpmVERQUlprPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6Itei15PXnyIsImZhbWlseV9uYW1lIjoi16nXp9eTIiwibG9jYWxlIjoiZW4iLCJpYXQiOjE2NDgxMDIzMDksImV4cCI6MTY0ODEwNTkwOX0.Z0XNsN3ECsetJECG5GhCy5G7HcvABXBVWpI9JB42FDHaIC86dZP4N1Vq2bu0vIWj3v7ahPtMSJV1pL9YzArpG94eWbEWWeFDJN5iZF94VB3EbYRYb1bIESknA885MIsNaPe0fGVhdUNl9-1R2cHJW2hk5_cpdkmTHCncAx3PhsWm9pPdWcdTXs0ggqKPNmu--xbyI2kn8wm4B_RW'
    db = DBService(app)
    # CREATE ALBUM
    # db.create_album(Album(
    #     owner_id=uid,
    #     name="Template",
    #     date_range=DateTimeRange(start=datetime(2022, 3, 18), end=datetime(2022, 3, 20)),
    # ))
    # UPLOAD IMAGE
    # db.upload_image(Image(
    #     owner_id=uid,
    #     file_name='img2',
    #     image_url='test.com',
    #     timestamp=datetime.now()
    # ))

    # https://oauth2.googleapis.com/tokeninfo?id_token=

    # get user + timestamps
    client = auth.Client(app)
    usr: UserRecord = client.get_user(uid)
    res = auth.verify_id_token(tkn)
    # res = client.verify_id_token(tkn)  # VERIFY ID TOKEN ###
    print(res)
    exit()
    q = usr.user_metadata.last_sign_in_timestamp
    print(datetime.fromtimestamp(q / 1e3))

    a: google.cloud.firestore_v1.client.Client = firestore.client(app)

    # albums = db.get_album_details(uid)
    # print(albums)
    # p = auth.Client(app)
    usr: UserRecord = client.get_user(uid)
    print(usr.email)

    # exit()

    b = a.collection('images').document('img2')
    print(b.get().to_dict()['containing_albums'])

    # imgs = db.get_album_content('f89StGP2SX9tWaPB4ckb')
    # print(imgs)


if __name__ == '__main__':
    main()
