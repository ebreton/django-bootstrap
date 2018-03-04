from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser

from dirtyfields import DirtyFieldsMixin


class User(AbstractUser):

    def __str__(self):
        return self.email


class Greeting(DirtyFieldsMixin, models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)

    def __unicode__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('crud:greeting-detail', args=[str(self.id)])

    class Meta:
        ordering = ['-id']


Greeting.mock_objects = Greeting.objects.db_manager('mock')
