from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import MembreCreationForm, ProjetCreationForm, TicketForm
from .models import Comment, Membre, Notification, Projet, Ticket


def admin_required(view):
    """Réserve une vue aux administrateurs (utilisateurs « staff »)."""

    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("Accès réservé aux administrateurs.")
        return view(request, *args, **kwargs)

    return wrapper


def membre_courant(user):
    return Membre.objects.filter(user=user).first()


def tickets_visibles(user):
    """Un administrateur voit tous les tickets, un membre seulement les siens."""
    if user.is_staff:
        return Ticket.objects.all()
    membre = membre_courant(user)
    if membre is None:
        return Ticket.objects.none()
    return Ticket.objects.filter(projet__membres=membre, membre=membre)


# ---------------------------------------------------------------- Authentification

def login_page(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user is not None:
            login(request, user)
            return redirect('blank')
        messages.error(request, "Identifiant ou mot de passe incorrect.")
    return render(request, 'signin.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------------------------------------------------------- Administration

@admin_required
def create_membre(request):
    if request.method == 'POST':
        form = MembreCreationForm(request.POST, request.FILES)
        if form.is_valid():
            membre = form.save()
            messages.success(request, f"Membre {membre} créé.")
            return redirect('create_membre')
    else:
        form = MembreCreationForm()
    membres = Membre.objects.select_related('user').order_by('nom')
    return render(request, 'ajouter_membre.html', {'form': form, 'membres': membres})


@admin_required
@require_POST
def delete_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    membre.user.delete()  # supprime aussi le membre (cascade)
    messages.success(request, "Membre supprimé.")
    return redirect('create_membre')


@admin_required
def create_projet(request):
    if request.method == 'POST':
        form = ProjetCreationForm(request.POST, request.FILES)
        if form.is_valid():
            projet = form.save()
            Notification.objects.create(user=request.user, message=f"Projet « {projet.nom} » créé.")
            messages.success(request, f"Projet « {projet.nom} » créé.")
            return redirect('projet')
    else:
        form = ProjetCreationForm()
    projets = Projet.objects.prefetch_related('membres').order_by('-date_debut')
    return render(request, 'projet.html', {'form': form, 'projets': projets})


# ---------------------------------------------------------------- Tableau de bord

def pourcentage(part, total):
    return round(part * 100 / total, 1) if total else 0


@login_required
def blank(request):
    """Tableau d'atelier : une colonne par état du workflow."""
    tickets = tickets_visibles(request.user).select_related('projet', 'membre').order_by('-date_creation', '-id')
    libelles = dict(Ticket.STATUS_CHOICES)
    ordre = ['declare', 'analyse', 'traitement', 'cloture', 'rejete']  # le rejet est une sortie latérale
    colonnes = [{'code': c, 'libelle': libelles[c], 'tickets': [t for t in tickets if t.etat == c]} for c in ordre]
    return render(request, 'blank.html', {'colonnes': colonnes, 'transitions': Ticket.TRANSITIONS})


@admin_required
def ticket_stats(request):
    data = {code: Ticket.objects.filter(etat=code).count() for code, _ in Ticket.STATUS_CHOICES}
    return JsonResponse(data)


@admin_required
def ticket_type_percentage(request):
    total = Ticket.objects.count()
    data = {
        'anomalies': pourcentage(Ticket.objects.filter(type='anomalie').count(), total),
        'parametrages': pourcentage(Ticket.objects.filter(type='parametrage').count(), total),
        'infos': pourcentage(Ticket.objects.filter(type='info').count(), total),
    }
    return JsonResponse(data)


@admin_required
def project_stats(request):
    project_data = {}
    for projet in Projet.objects.all():
        total = projet.ticket_set.count()
        if total:
            project_data[projet.nom] = pourcentage(projet.ticket_set.filter(etat='cloture').count(), total)
    return JsonResponse({'total_projects': Projet.objects.count(), 'project_data': project_data})


# ---------------------------------------------------------------- Projets et tickets

@login_required
def member_projects(request):
    membre = membre_courant(request.user)
    projects = Projet.objects.filter(membres=membre) if membre else Projet.objects.none()
    return render(request, 'projet.html', {'projects': projects})


def filtrer_et_trier(request, tickets):
    project_filter = request.GET.get('project')
    status_filter = request.GET.get('status')
    if project_filter:
        tickets = tickets.filter(projet__id=project_filter)
    if status_filter:
        tickets = tickets.filter(etat=status_filter)
    sort_by = request.GET.get('sort_by', 'date_creation')
    if sort_by == 'alphabetical':
        tickets = tickets.order_by('Intitulé')
    else:
        sort_by = 'date_creation'
        tickets = tickets.order_by('-date_creation', '-moment_creation')
    return tickets, sort_by


@login_required
def tickets(request):
    membre = membre_courant(request.user)
    if request.user.is_staff:
        projects = Projet.objects.all()
    elif membre:
        projects = membre.projet_set.all()
    else:
        return HttpResponseForbidden("Ce compte n'est rattaché à aucun membre.")

    form = TicketForm(projets=projects)
    if request.method == 'POST':
        if membre is None:
            return HttpResponseForbidden("Seuls les membres peuvent déclarer un ticket.")
        form = TicketForm(request.POST, projets=projects)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.membre = membre
            ticket.save()
            Notification.objects.create(user=request.user, message=f"Ticket « {ticket.Intitulé} » créé.")
            messages.success(request, "Ticket déclaré.")
            return redirect('tickets')

    liste, sort_by = filtrer_et_trier(request, tickets_visibles(request.user).select_related('projet', 'membre'))
    page_obj = Paginator(liste, 10).get_page(request.GET.get('page'))
    return render(request, 'tickets.html', {
        'page_obj': page_obj, 'form': form, 'projects': projects, 'sort_by': sort_by,
    })


@login_required
def list_tickets(request):
    # Ancienne page « tickets créés » : la liste des tickets la remplace (mêmes filtres).
    query = request.GET.urlencode()
    return redirect(reverse('tickets') + (f'?{query}' if query else ''))


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(tickets_visibles(request.user), id=ticket_id)
    return render(request, 'ticket_detail.html', {'ticket': ticket})


@admin_required
@require_POST
def update_ticket_state(request):
    ticket = Ticket.objects.filter(id=request.POST.get('ticket_id')).first()
    if ticket is None:
        return JsonResponse({'status': 'error', 'message': 'Ticket introuvable'}, status=404)
    new_state = request.POST.get('new_state')
    try:
        ticket.changer_etat(new_state, remarque=request.POST.get('remark'))
    except ValueError as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)
    if ticket.membre:
        Notification.objects.create(
            user=ticket.membre.user,
            message=f"Le ticket « {ticket.Intitulé} » est passé à « {ticket.get_etat_display()} ».",
        )
    return JsonResponse({'status': 'success', 'etat': ticket.etat})


@login_required
@require_POST
def add_comment(request, ticket_id):
    ticket = get_object_or_404(tickets_visibles(request.user), id=ticket_id)
    content = (request.POST.get('content') or '').strip()
    if content:
        Comment.objects.create(ticket=ticket, user=request.user, content=content)
    retour = request.META.get('HTTP_REFERER')
    if retour and url_has_allowed_host_and_scheme(retour, allowed_hosts={request.get_host()}):
        return redirect(retour)
    return redirect('ticket_detail', ticket_id=ticket.id)


@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})
