from django.db import models

# Create your models here.

class Quotes(models.Model):

    def __str__(self):
        return f'Quote {self.author}'

    author = models.CharField(max_length=500)
    text = models.CharField(max_length=4000)
    biolink = models.CharField(max_length=500)
    author_born = models.CharField(max_length=1000)
    author_location = models.CharField(max_length=1000)
