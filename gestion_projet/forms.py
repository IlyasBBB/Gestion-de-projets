from django import forms
from django.contrib.auth.models import User
from .models import Membre, Projet, food

class MembreCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Membre
        fields = ['username', 'password', 'nom', 'prenom', 'telephone', 'email', 'profil']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password']
        )
        membre = Membre(
            user=user,
            nom=self.cleaned_data['nom'],
            prenom=self.cleaned_data['prenom'],
            telephone=self.cleaned_data['telephone'],
            email=self.cleaned_data['email'],
            profil=self.cleaned_data['profil']
        )
        if commit:
            user.save()
            membre.save()
        return membre
    

class ProjetCreationForm(forms.ModelForm):
    date_debut = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    date_fin = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    
    class Meta:
        model = Projet
        fields = ['nom', 'description', 'date_debut', 'date_fin', 'membres', 'file']

from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['projet', 'type', 'Intitulé', 'description']

from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']



