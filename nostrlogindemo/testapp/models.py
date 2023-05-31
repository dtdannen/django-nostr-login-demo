from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=150, blank=True, null=True)
    lud16 = models.CharField(max_length=150, blank=True, null=True)
