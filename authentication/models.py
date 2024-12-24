from django.contrib.auth.models import AbstractUser
from django.db import models
from authentication.manager import CustomUserManager


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, TimestampedModel):  #extend AbstractUser to retain the default features while adding your own
    username = None    
    email = models.EmailField(unique=True)

    # Custom manager
    objects = CustomUserManager()   #CustomUserManager is a custom class (defined separately) that provides methods for creating both regular users and superusers.

    USERNAME_FIELD = 'email'  # Use email as the username field
    
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


class Blogpost(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="blogs", null=True, blank=True)
    likes = models.ManyToManyField(User, related_name="like_blogs", blank=True)

    def total_like(self):
        return self.likes.count()
 
    def __str__(self):
        return self.title


class Comment(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blogpost, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()


class Like(TimestampedModel):
    blog_post = models.ForeignKey(Blogpost, on_delete=models.CASCADE, related_name="like")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
