from django.contrib import admin
from app import models

# Register your models here.
admin.site.register(models.Quastion)
admin.site.register(models.Tag)
admin.site.register(models.Answer)
admin.site.register(models.Profile)
admin.site.register(models.AnswerLike)
admin.site.register(models.QuastionLike)
