from django.contrib import admin
from . import models

admin.site.register(models.LibrarianItem)
admin.site.register(models.Profile)
admin.site.register(models.Collection)
admin.site.register(models.CollectionAccessRequest)
admin.site.register(models.Review)
admin.site.register(models.Notification)
admin.site.register(models.ItemAccessRequest)
admin.site.register(models.ItemReturnRequest)
admin.site.register(models.LibrarianItemImage)
