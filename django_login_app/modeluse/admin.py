from django.contrib import admin

from .models import Account,NiftyFile,ObjFile
admin.site.register(Account)
admin.site.register(NiftyFile)
admin.site.register(ObjFile)