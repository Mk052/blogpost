# Generated by Django 5.1.4 on 2024-12-23 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0009_rename_comments_comment_content"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="blog_post",
            new_name="blog",
        ),
    ]
