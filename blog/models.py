from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 
from catalog.models import Substitute


class Comment(models.Model):
    content = models.TextField()
    date_added = models.DateTimeField(default=timezone.now,
                                verbose_name="Date d'ajout")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    substitute = models.ForeignKey(Substitute, on_delete=models.CASCADE)

    def __str__(self):
        return self.author.username