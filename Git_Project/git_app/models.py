from django.db import models

# Create your models here.

# create a model (table) named UserName using django Model
class UserName(models.Model):
    # create a char field named username with following properties
    username = models.CharField(max_length=256, unique=True)

    # send username whenever the model is called or reffered
    def __str__(self):
        return self.username