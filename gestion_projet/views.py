from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import MembreCreationForm, ProjetCreationForm, TicketForm
from .models import Projet, Membre, Ticket, Comment, Notification
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST




def login_page(request):
    if request.method == "POST":
        un = request.POST.get('username')
        pw = request.POST.get('password')    
    
        user = authenticate(request, username=un, password=pw)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/admin/')
            elif user.is_staff:
                login(request,user)
                return redirect('/blank/')
            else:
                login(request, user)
                return redirect('/blank/')
               
    context = {
        'timestamp': now().strftime('%Y%m%d%H%M%S'),
        
    }
    
    return render(request, 'signin.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')


def create_membre(request):
    if request.method == 'POST':
        form = MembreCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('create_membre')  
    else:
        form = MembreCreationForm()
    
    membres = Membre.objects.all()
    return render(request, 'ajouter_membre.html', {'form': form, 'membres': membres})

def delete_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    membre.delete()
    return redirect('create_membre')


################################## DACHBOARD #######################################


from django.shortcuts import render
from django.http import JsonResponse
from .models import Ticket, Projet
def ticket_stats(request):
    traitement = Ticket.objects.filter(etat='traitement').count()
    rejete = Ticket.objects.filter(etat='rejete').count()
    cloture = Ticket.objects.filter(etat='cloture').count()

    data = {
        'traitement': traitement,
        'rejete': rejete,
        'cloture': cloture,
    }
    
    return JsonResponse(data)

def ticket_type_percentage(request):
    total_tickets = Ticket.objects.count()
    anomalies = Ticket.objects.filter(type='anomalie').count()
    parametrages = Ticket.objects.filter(type='parametrage').count()
    infos = Ticket.objects.filter(type='info').count()

    data = {
        'anomalies': (anomalies / total_tickets) * 100,
        'parametrages': (parametrages / total_tickets) * 100,
        'infos': (infos / total_tickets) * 100
    }
    return JsonResponse(data)

def project_stats(request):
    total_projects = Projet.objects.count()
    tickets = Ticket.objects.all()
    projects = Projet.objects.all()

    project_data = {}
    for project in projects:
        total = tickets.filter(projet=project).count()
        closed = tickets.filter(projet=project, etat='cloture').count()
        if total > 0:
            project_data[project.nom] = (closed / total) * 100

    data = {
        'total_projects': total_projects,
        'project_data': project_data
    }
    return JsonResponse(data)



####################################################################################
def blank(request):
    return render(request, 'blank.html')

from .models import Notification  # Assurez-vous d'importer le modèle Notification

def create_projet(request):
    if request.method == 'POST':
        form = ProjetCreationForm(request.POST, request.FILES)
        if form.is_valid():
            projet = form.save()
            Notification.objects.create(
                user=request.user,
                message=f"Projet '{projet.nom}' a été créé."
            )
            return redirect('projet')
    else:
        form = ProjetCreationForm()
    
    projets = Projet.objects.all()
    return render(request, 'projet.html', {'form': form, 'projets': projets})



############## Pour Membre


@login_required
def member_projects(request):
    member = Membre.objects.get(user=request.user)
    projects = Projet.objects.filter(membres=member)
    return render(request, 'projet.html', {'projects': projects})






from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TicketForm
from .models import Ticket, Membre

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Ticket, Projet, Membre
from .forms import TicketForm

from django.core.paginator import Paginator
from django.db.models import Q

def tickets(request):
    if request.user.is_staff:
        tickets = Ticket.objects.all()
        projects = Projet.objects.all()
    else:
        try:
            member = Membre.objects.get(user=request.user)
            projects = member.projet_set.all()
            tickets = Ticket.objects.filter(projet__in=projects, membre=member)
        except Membre.DoesNotExist:
            return redirect('some_error_page')

    project_filter = request.GET.get('project')
    status_filter = request.GET.get('status')

    if project_filter:
        tickets = tickets.filter(projet__id=project_filter)
    if status_filter:
        tickets = tickets.filter(etat=status_filter)

    sort_by = request.GET.get('sort_by', 'date_creation')
    if sort_by == 'alphabetical':
        tickets = tickets.order_by('Intitulé')
    elif sort_by == 'date_creation':
        tickets = tickets.order_by('-date_creation')

    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.membre = Membre.objects.get(user=request.user)
            ticket.save()
            Notification.objects.create(
                user=request.user,
                message=f"Ticket '{ticket.Intitulé}' a été créé."
            )
            return redirect('tickets')
    else:
        form = TicketForm()
    return render(request, 'tickets.html', {'page_obj': page_obj, 'form': form, 'projects': projects, 'sort_by': sort_by})





@require_POST
def update_ticket_state(request):
    ticket_id = request.POST.get('ticket_id')
    new_state = request.POST.get('new_state')
    remark = request.POST.get('remark')

    try:
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.etat = new_state
        if new_state == 'rejete' and remark:
            ticket.remarks = remark
        ticket.save()
        Notification.objects.create(
            user=ticket.membre.user,
            message=f"Le statut du ticket '{ticket.Intitulé}' a été changé à '{new_state}'."
        )
        return JsonResponse({'status': 'success'})
    except Ticket.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Ticket not found'}, status=404)




@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        if 'status_update' in request.POST:
            new_state = request.POST.get('new_state')
            ticket.etat = new_state
            if new_state == 'rejete':
                ticket.remarks = request.POST.get('remarks')
            ticket.save()
        elif 'add_comment' in request.POST:
            new_comment = request.POST.get('comment')
            ticket.comments = ticket.comments + "\n" + new_comment if ticket.comments else new_comment
            ticket.save()
        return redirect('ticket_detail', ticket_id=ticket.id)

    return render(request, 'ticket_detail.html', {'ticket': ticket})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Ticket, Projet, Membre
from django.core.paginator import Paginator

@login_required
def list_tickets(request):
    try:
        member = Membre.objects.get(user=request.user)
        projects = member.projet_set.all()
        tickets = Ticket.objects.filter(projet__in=projects, membre=member)
    except Membre.DoesNotExist:
        return redirect('some_error_page')

    project_id = request.GET.get('project')
    status = request.GET.get('status')
    sort_by = request.GET.get('sort_by')
    sort_order = request.GET.get('sort_order', 'asc')  # 'asc' pour croissant, 'desc' pour décroissant

    if project_id:
        tickets = tickets.filter(projet_id=project_id)
    
    if status:
        tickets = tickets.filter(etat=status)
    
    if sort_by:
        if sort_by not in ['date_creation', 'Intitulé']:
            sort_by = 'date_creation'  # Valeur par défaut si un champ invalide est fourni
        if sort_order == 'desc':
            sort_by = '-' + sort_by
        tickets = tickets.order_by(sort_by)
    
    paginator = Paginator(tickets, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'list_tickets.html', {'page_obj': page_obj, 'projects': projects})



    




from django.http import HttpResponseRedirect

@require_POST
@login_required
def add_comment(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    content = request.POST.get('content')
    if content:
        Comment.objects.create(ticket=ticket, user=request.user, content=content)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def some_view(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'some_template.html', {'notifications': notifications})
