from django.contrib import admin
from .models import Course,Category,Module,Content,Tier

admin.site.register(Course)
admin.site.register(Category)
admin.site.register(Module)
admin.site.register(Content)
admin.site.register(Tier)