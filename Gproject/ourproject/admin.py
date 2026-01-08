from django.contrib import admin
from .models import Profile, Order, MenuItem

# Register your models here.
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(MenuItem)
