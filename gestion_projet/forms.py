from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from .models import Comment, Membre, Projet, Ticket


class MembreCreationForm(forms.ModelForm):
    username = forms.CharField(label="Identifiant", max_length=150)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

    class Meta:
        model = Membre
        fields = ['username', 'password', 'nom', 'prenom', 'telephone', 'email', 'profil']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Cet identifiant est déjà utilisé.")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    @transaction.atomic
    def save(self, commit=True):
        membre = super().save(commit=False)
        membre.user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
        )
        if commit:
            membre.save()
        return membre


class ProjetCreationForm(forms.ModelForm):
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Projet
        fields = ['nom', 'description', 'date_debut', 'date_fin', 'membres', 'file']

    def clean(self):
        cleaned = super().clean()
        debut, fin = cleaned.get('date_debut'), cleaned.get('date_fin')
        if debut and fin and fin < debut:
            self.add_error('date_fin', "La date de fin doit suivre la date de début.")
        return cleaned


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['projet', 'type', 'Intitulé', 'description']

    def __init__(self, *args, projets=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Un membre ne peut déclarer un ticket que sur un projet auquel il est affecté.
        if projets is not None:
            self.fields['projet'].queryset = projets


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
