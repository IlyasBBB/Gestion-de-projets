from django.conf import settings

from .models import Notification
from .views import tickets_visibles


def notifications(request):
    """Notifications non lues, voyant andon (tickets en attente d'analyse) et mode démo."""
    contexte = {'notifications': [], 'andon': 0, 'demo': settings.DEMO_MODE}
    if request.user.is_authenticated:
        contexte['notifications'] = Notification.objects.filter(user=request.user, is_read=False)[:8]
        contexte['andon'] = tickets_visibles(request.user).filter(etat='declare').count()
    return contexte
