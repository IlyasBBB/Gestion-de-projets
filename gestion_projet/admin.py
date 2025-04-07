from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Admin, Membre, Ticket, Projet, food, Notification

# Dé-enregistrement du modèle User si nécessaire
admin.site.unregister(User)

# Ré-enregistrement du modèle User avec un admin personnalisé si nécessaire
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass

# Enregistrement des autres modèles
admin.site.register(Admin)
admin.site.register(Membre)
admin.site.register(Ticket)
admin.site.register(Projet)

admin.site.register(Notification)
admin.site.register(food)



