from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('logout/', views.logout_view, name='mylogout'),
    path('create-membre/', views.create_membre, name='create_membre'),
    path('delete-membre/<int:membre_id>/', views.delete_membre, name='delete_membre'),
    path('blank/', views.blank, name='blank'),
    path('projet/', views.create_projet, name='projet'),
    path('my-projects/', views.member_projects, name='member-projects'),
    path('tickets/', views.tickets, name='tickets'),
    path('update_ticket_state/', views.update_ticket_state, name='update_ticket_state'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:ticket_id>/add_comment/', views.add_comment, name='add_comment'),
    path('list_tickets/', views.list_tickets, name='list_tickets'),

    path('ticket-stats/', views.ticket_stats, name='ticket-stats'),
    path('ticket-type-percentage/', views.ticket_type_percentage, name='ticket-type-percentage'),
    path('project-stats/', views.project_stats, name='project-stats'),


]
