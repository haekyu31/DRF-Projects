from django.contrib import admin
# 작성한 models에서 Todo를 admin으로 확인할수 있도록
from .models import Todo

# Register your models here.
admin.site.register(Todo)