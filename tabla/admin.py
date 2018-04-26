from django.contrib import admin

# Register your models here.
from .models import Tabla,Post,Ideja

admin.site.register(Tabla)
admin.site.register(Post)
admin.site.register(Ideja)