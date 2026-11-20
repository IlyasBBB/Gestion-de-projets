from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import TicketForm
from .models import Admin, Comment, Membre, Notification, Projet, Ticket


def creer_membre(username):
    user = User.objects.create_user(username=username, password='motdepasse-test-123')
    return Membre.objects.create(user=user, nom=username.title(), prenom='Test',
                                 telephone='0600000000', email=f'{username}@exemple.test')


class DonneesDeBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        admin_user = User.objects.create_user(username='admin', password='motdepasse-test-123')
        Admin.objects.create(user=admin_user, nom='Admin', prenom='Test',
                             telephone='0600000000', email='admin@exemple.test')
        cls.admin_user = admin_user
        cls.alice = creer_membre('alice')
        cls.bob = creer_membre('bob')
        cls.projet_a = Projet.objects.create(nom='Projet A', description='-',
                                             date_debut=date(2024, 7, 1), date_fin=date(2024, 8, 15))
        cls.projet_b = Projet.objects.create(nom='Projet B', description='-',
                                             date_debut=date(2024, 7, 1), date_fin=date(2024, 8, 15))
        cls.projet_a.membres.add(cls.alice, cls.bob)
        cls.projet_b.membres.add(cls.bob)

    def nouveau_ticket(self, membre=None, projet=None, etat='declare'):
        return Ticket.objects.create(projet=projet or self.projet_a, type='anomalie', etat=etat,
                                     Intitulé='Écran figé', description='<p>-</p>',
                                     membre=membre or self.alice)

    def connecter(self, user):
        self.client.force_login(user)


class WorkflowTicketTests(DonneesDeBase):
    def test_un_ticket_commence_a_declare(self):
        self.assertEqual(self.nouveau_ticket().etat, 'declare')

    def test_parcours_complet_jusqu_a_cloture(self):
        ticket = self.nouveau_ticket()
        for etat in ('analyse', 'traitement', 'cloture'):
            ticket.changer_etat(etat)
        ticket.refresh_from_db()
        self.assertEqual(ticket.etat, 'cloture')
        self.assertEqual(ticket.etats_suivants(), [])

    def test_saut_d_etape_interdit(self):
        ticket = self.nouveau_ticket()
        with self.assertRaises(ValueError):
            ticket.changer_etat('cloture')
        ticket.refresh_from_db()
        self.assertEqual(ticket.etat, 'declare')

    def test_rejet_possible_seulement_apres_analyse(self):
        ticket = self.nouveau_ticket()
        self.assertFalse(ticket.peut_passer_a('rejete'))
        ticket.changer_etat('analyse')
        self.assertTrue(ticket.peut_passer_a('rejete'))

    def test_rejet_sans_remarque_refuse(self):
        ticket = self.nouveau_ticket(etat='analyse')
        with self.assertRaises(ValueError):
            ticket.changer_etat('rejete', remarque='   ')

    def test_rejet_enregistre_la_remarque(self):
        ticket = self.nouveau_ticket(etat='analyse')
        ticket.changer_etat('rejete', remarque='Doublon du ticket 12')
        ticket.refresh_from_db()
        self.assertEqual((ticket.etat, ticket.remarks), ('rejete', 'Doublon du ticket 12'))

    def test_etat_inconnu_refuse(self):
        with self.assertRaises(ValueError):
            self.nouveau_ticket().changer_etat('n_importe_quoi')


class ChangementEtatViaApiTests(DonneesDeBase):
    url = reverse('update_ticket_state')

    def test_admin_change_l_etat_et_le_membre_est_notifie(self):
        ticket = self.nouveau_ticket()
        self.connecter(self.admin_user)
        reponse = self.client.post(self.url, {'ticket_id': ticket.id, 'new_state': 'analyse'})
        self.assertEqual(reponse.json()['status'], 'success')
        ticket.refresh_from_db()
        self.assertEqual(ticket.etat, 'analyse')
        self.assertTrue(Notification.objects.filter(user=self.alice.user).exists())

    def test_transition_interdite_renvoie_400(self):
        ticket = self.nouveau_ticket()
        self.connecter(self.admin_user)
        reponse = self.client.post(self.url, {'ticket_id': ticket.id, 'new_state': 'cloture'})
        self.assertEqual(reponse.status_code, 400)

    def test_un_membre_ne_peut_pas_changer_l_etat(self):
        ticket = self.nouveau_ticket()
        self.connecter(self.alice.user)
        reponse = self.client.post(self.url, {'ticket_id': ticket.id, 'new_state': 'analyse'})
        self.assertEqual(reponse.status_code, 403)
        ticket.refresh_from_db()
        self.assertEqual(ticket.etat, 'declare')

    def test_ticket_introuvable(self):
        self.connecter(self.admin_user)
        reponse = self.client.post(self.url, {'ticket_id': 9999, 'new_state': 'analyse'})
        self.assertEqual(reponse.status_code, 404)


class ControleAccesTests(DonneesDeBase):
    def test_pages_protegees_redirigent_vers_la_connexion(self):
        for nom in ('blank', 'tickets', 'list_tickets', 'projet', 'create_membre'):
            reponse = self.client.get(reverse(nom))
            self.assertEqual(reponse.status_code, 302, nom)
            self.assertTrue(reponse.url.startswith(reverse('login')), nom)

    def test_pages_admin_interdites_aux_membres(self):
        self.connecter(self.alice.user)
        for nom in ('create_membre', 'projet', 'ticket-stats', 'project-stats'):
            self.assertEqual(self.client.get(reverse(nom)).status_code, 403, nom)

    def test_un_membre_ne_peut_pas_supprimer_un_membre(self):
        self.connecter(self.alice.user)
        reponse = self.client.post(reverse('delete_membre', args=[self.bob.id]))
        self.assertEqual(reponse.status_code, 403)
        self.assertTrue(Membre.objects.filter(id=self.bob.id).exists())

    def test_suppression_par_admin_supprime_aussi_le_compte(self):
        self.connecter(self.admin_user)
        self.client.post(reverse('delete_membre', args=[self.bob.id]))
        self.assertFalse(Membre.objects.filter(id=self.bob.id).exists())
        self.assertFalse(User.objects.filter(username='bob').exists())

    def test_suppression_refusee_en_get(self):
        self.connecter(self.admin_user)
        self.assertEqual(self.client.get(reverse('delete_membre', args=[self.bob.id])).status_code, 405)


class VisibiliteTicketsTests(DonneesDeBase):
    def test_un_membre_ne_voit_pas_le_ticket_d_un_autre(self):
        ticket_de_bob = self.nouveau_ticket(membre=self.bob)
        self.connecter(self.alice.user)
        self.assertEqual(self.client.get(reverse('ticket_detail', args=[ticket_de_bob.id])).status_code, 404)

    def test_un_membre_voit_son_ticket(self):
        ticket = self.nouveau_ticket()
        self.connecter(self.alice.user)
        self.assertEqual(self.client.get(reverse('ticket_detail', args=[ticket.id])).status_code, 200)

    def test_l_admin_voit_tous_les_tickets(self):
        self.nouveau_ticket()
        self.nouveau_ticket(membre=self.bob, projet=self.projet_b)
        self.connecter(self.admin_user)
        reponse = self.client.get(reverse('tickets'))
        self.assertEqual(reponse.context['page_obj'].paginator.count, 2)

    def test_filtre_par_statut(self):
        self.nouveau_ticket()
        self.nouveau_ticket(etat='analyse')
        self.connecter(self.admin_user)
        reponse = self.client.get(reverse('tickets'), {'status': 'analyse'})
        self.assertEqual(reponse.context['page_obj'].paginator.count, 1)

    def test_commentaire_impossible_sur_un_ticket_invisible(self):
        ticket_de_bob = self.nouveau_ticket(membre=self.bob)
        self.connecter(self.alice.user)
        self.client.post(reverse('add_comment', args=[ticket_de_bob.id]), {'content': 'Bonjour'})
        self.assertFalse(Comment.objects.exists())

    def test_commentaire_sur_son_ticket(self):
        ticket = self.nouveau_ticket()
        self.connecter(self.alice.user)
        self.client.post(reverse('add_comment', args=[ticket.id]), {'content': 'Capture jointe'})
        self.assertEqual(ticket.comments.get().content, 'Capture jointe')


class DeclarationTicketTests(DonneesDeBase):
    def test_le_formulaire_ne_propose_que_les_projets_du_membre(self):
        form = TicketForm(projets=self.alice.projet_set.all())
        self.assertQuerySetEqual(form.fields['projet'].queryset, [self.projet_a])

    def test_declaration_sur_un_projet_non_affecte_refusee(self):
        self.connecter(self.alice.user)
        self.client.post(reverse('tickets'), {'projet': self.projet_b.id, 'type': 'info',
                                              'Intitulé': 'Question', 'description': '<p>?</p>'})
        self.assertFalse(Ticket.objects.exists())

    def test_declaration_valide(self):
        self.connecter(self.alice.user)
        self.client.post(reverse('tickets'), {'projet': self.projet_a.id, 'type': 'info',
                                              'Intitulé': 'Question', 'description': '<p>?</p>'})
        ticket = Ticket.objects.get()
        self.assertEqual((ticket.membre, ticket.etat), (self.alice, 'declare'))


class StatistiquesTests(DonneesDeBase):
    def test_statistiques_sans_aucun_ticket(self):
        self.connecter(self.admin_user)
        reponse = self.client.get(reverse('ticket-type-percentage'))
        self.assertEqual(reponse.json(), {'anomalies': 0, 'parametrages': 0, 'infos': 0})

    def test_compte_par_etat(self):
        self.nouveau_ticket()
        self.nouveau_ticket(etat='cloture')
        self.connecter(self.admin_user)
        data = self.client.get(reverse('ticket-stats')).json()
        self.assertEqual((data['declare'], data['cloture'], data['analyse']), (1, 1, 0))

    def test_taux_de_cloture_par_projet(self):
        self.nouveau_ticket(etat='cloture')
        self.nouveau_ticket()
        self.connecter(self.admin_user)
        data = self.client.get(reverse('project-stats')).json()
        self.assertEqual(data['project_data'], {'Projet A': 50.0})


class ConnexionTests(DonneesDeBase):
    def test_mauvais_mot_de_passe(self):
        reponse = self.client.post(reverse('login'), {'username': 'alice', 'password': 'faux'})
        self.assertContains(reponse, 'Identifiant ou mot de passe incorrect')

    def test_connexion_reussie(self):
        reponse = self.client.post(reverse('login'), {'username': 'alice', 'password': 'motdepasse-test-123'})
        self.assertRedirects(reponse, reverse('blank'), fetch_redirect_response=False)


class InterfaceTests(DonneesDeBase):
    def test_script_retire_de_la_description(self):
        self.connecter(self.alice.user)
        self.client.post(reverse('tickets'), {'projet': self.projet_a.id, 'type': 'info', 'Intitulé': 'XSS',
                                              'description': '<p>ok</p><script>alert(1)</script>'})
        self.assertEqual(Ticket.objects.get().description, '<p>ok</p>')

    def test_tableau_range_les_tickets_par_etat(self):
        ticket = self.nouveau_ticket(etat='analyse')
        self.connecter(self.admin_user)
        colonnes = {c['code']: c['tickets'] for c in self.client.get(reverse('blank')).context['colonnes']}
        self.assertEqual(list(colonnes), ['declare', 'analyse', 'traitement', 'cloture', 'rejete'])
        self.assertEqual(colonnes['analyse'], [ticket])
        self.assertContains(self.client.get(reverse('blank')), ticket.numero)
