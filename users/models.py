from django.db import models
from django.contrib.auth.models import User


class EditProfile(models.Model):
    about_me = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.about_me