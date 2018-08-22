from django.contrib import admin
from .models import *

    
# Register your models here.
admin.site.register(Categories)
admin.site.register(Secretaries)
admin.site.register(Datasets)
admin.site.register(Users)
admin.site.register(Token)
admin.site.register(ETLS)