from django.db import models

# Create your models here.
class UserName(models.Model):
    username = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.username