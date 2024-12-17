from django.contrib.auth.models import AbstractUser
from django.db import models
from authentication.manager import CustomUserManager


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, TimestampedModel):     #extend AbstractUser to retain the default features while adding your own
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Custom manager
    objects = CustomUserManager()   #CustomUserManager is a custom class (defined separately) that provides methods for creating both regular users and superusers.

    USERNAME_FIELD = 'email'  # Use email as the username field
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    


class Blogpost(TimestampedModel):
    #user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    content=models.TextField()
    category=models.CharField(max_length=100)

class Comment(TimestampedModel):
    blog_post=models.ForeignKey(Blogpost,on_delete=models.CASCADE,related_name="comment")
    comments=models.TextField()

class Like(TimestampedModel):
    blog_post=models.ForeignKey(Blogpost,on_delete=models.CASCADE,related_name="like")
    user=models.ForeignKey(User,on_delete=models.CASCADE)
