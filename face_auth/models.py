from uuid import uuid4
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

import face_auth

def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.username,filename)

class User(AbstractUser):
    uid = models.UUIDField(default=uuid4,primary_key=True,editable=False)
    face_image = models.FileField(upload_to=user_directory_path)
    img = models.TextField(default='')
    face_auth = models.BooleanField(default=False)

    def __str__(self):
        return self.username