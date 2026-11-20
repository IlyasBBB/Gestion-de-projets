from django.contrib import admin

from .models import Admin, Comment, Membre, Notification, Projet, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('Intitulé', 'projet', 'type', 'etat', 'membre', 'date_creation')
    list_filter = ('etat', 'type', 'projet')
    search_fields = ('Intitulé',)


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_debut', 'date_fin')
    filter_horizontal = ('membres',)


admin.site.register(Admin)
admin.site.register(Membre)
admin.site.register(Comment)
admin.site.register(Notification)
