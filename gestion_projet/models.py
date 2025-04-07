from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    profil = models.ImageField(upload_to='uploads/Manager_', default='uploads/Manager_/unknown_pdp.png')

    def save(self, *args, **kwargs):
        self.user.is_staff = True
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Membre(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    profil = models.ImageField(upload_to='uploads/Membre', default='uploads/Membre/unknown_pdp.jpg')

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Projet(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    membres = models.ManyToManyField(Membre)
    file = models.FileField(null=True, blank=True)
    def __str__(self):
        return self.nom
    
    
class Ticket(models.Model):
    TYPE_CHOICES = [
        ('anomalie', 'Anomalie'),
        ('parametrage', 'Paramétrage Système'),
        ('info', 'Demande d\'Information'),
    ]
    STATUS_CHOICES = [
        ('declare', 'Déclaré'),
        ('analyse', 'En cours d\'analyse'),
        ('traitement', 'En cours de traitement'),
        ('rejete', 'Rejeté'),
        ('cloture', 'Cloturé')
    ]

    projet = models.ForeignKey('Projet', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    etat = models.CharField(max_length=20, choices=STATUS_CHOICES, default='declare')
    Intitulé = models.CharField(max_length=200)
    description = HTMLField()
    membre = models.ForeignKey('Membre', on_delete=models.CASCADE, null=True)
    date_creation = models.DateField(auto_now_add=True)
    moment_creation = models.TimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.Intitulé

class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.ticket.Intitulé}'
    
    from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    

class food(models.Model):

    name = models.TextField()
    ingredient1 = models.TextField()
    ingredient2 = models.TextField()
    ingredient3 = models.TextField()
    ingredient4 = models.TextField()
    duration = models.TimeField()

    def __str__(self):
        return self.name