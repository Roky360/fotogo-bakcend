import firebase_admin
from firebase_admin import credentials

from ..framework import Framework

cred = credentials.Certificate("serviceAccountKey.json")
firebase_app: firebase_admin.App = firebase_admin.initialize_app(cred, {
    'storageBucket': 'fotogo-5e99f.appspot.com'
})
app = Framework(firebase_app)

import fotogo_networking.endpoints.albums_endpoints
import fotogo_networking.endpoints.users_endpoints
import fotogo_networking.endpoints.images_endpoints
