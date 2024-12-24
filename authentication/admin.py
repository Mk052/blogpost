from django.contrib import admin
from authentication.models import *

admin.site.register(User)
admin.site.register(Blogpost)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Like)



# Register your models here.
