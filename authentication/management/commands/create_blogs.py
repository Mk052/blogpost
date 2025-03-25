from django.core.management.base import BaseCommand
from faker import Faker 
from authentication.models import User, Category, Blogpost
import random


class Command(BaseCommand):
    help = 'Creating the 10 blogs'

    def handle(self, *args, **kwargs):
        fake = Faker()

        for i in range(10):
            user = User.objects.create(email=fake.email(), password="Password123")
            self.stdout.write(f'successfully created user, {user.email}!')

        # Generate random data using Faker
        categories = []
        for i in range(10):
            category = Category.objects.create(name=fake.word())
            categories.append(category)
            self.stdout.write(f'successfully created category, {category.name}!')

        users = User.objects.filter(is_staff=False) 
        for category in categories:
            blog = Blogpost.objects.create(title=fake.word(), content=fake.paragraph(), user=random.choice(users), category=category)
            self.stdout.write(f'successfully created a new blog, {blog.title}!')
