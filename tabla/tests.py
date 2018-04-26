from django.test import TestCase
from django.urls import reverse
from django.urls import resolve

from .views import home,IdejeNaTabli
from .models import Tabla, Ideja, Post

class HomeTests(TestCase):
    def test_home_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_url_resolvers_home_view(self):
        view = resolve('/')
        self.assertEqual(view.func,home)

class IdejeZaAktivnost(TestCase):
    def setUp(self):
        Tabla.objects.create(name='MTB',description='Čez drn in strn.')

    # is testing if Django is returning a status code 200(success)
    # for an existing Board.
    def test_Ideje_na_tabeli_preveri_uspeh_kode(self):
        url = reverse('IdejeNaTabli',kwargs={'pk':1})
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)

    def test_ideje_ne_najde_na_tabeli(self):
        url = reverse('IdejeNaTabli',kwargs={'pk':999})
        response = self.client.get(url)
        self.assertEqual(response.status_code,404)

    # is testing if Django is using the correct viewfunction to render the topics
    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/ideje/1')
        self.assertEquals(view.func, IdejeNaTabli)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse('IdejeNaTabli', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))


class HomeTest(TestCase):
    def setUp(self):
        self.tabla = Tabla.objects.create(name='MTB',description='Čez drn in strn.')
        url = reverse('home')
        self.response = self.client.get(url)

    def preveri_statusno_kodo_home_starni(self):
        self.assertEqual(self.response.status_code,200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('IdejeNaTabli', kwargs={'pk': self.tabla.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))

    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse('IdejeNaTabli', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))

class TestiranjeNoveIdeje(TestCase):
    def setUp(self):
        Tabla.objects.create(name='Ostalo',description='Testiranje nove ideje')

    def se_nova_ideja_nalozi(self):
        url = reverse('novaIdeja',kwargs={'pk':1})
        response=self.create.get(url)
        self.assertEqual(response.status_code,200)

    def testiranje_nove_teme_ki_ne_obstatja(self):
        url = reverse('novaIdeja', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_novaideja_url_resolves_view(self):
        view = resolve('ideje/1/novaideja/')
        self.assertEquals(view.func, home)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        new_topic_url = reverse('novaIdeja', kwargs={'pk': 1})
        board_topics_url = reverse('IdejeNaTabli', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))


    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('IdejeNaTabli', kwargs={'pk': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('novaIdeja', kwargs={'pk': 1})

        response = self.client.get(board_topics_url)

        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))

    def test_csrf(self):
        url = reverse('novaIdeja', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('novaIdeja', kwargs={'pk': 1})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        response = self.client.post(url, data)
        self.assertTrue(Ideja.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('novaIdeja', kwargs={'pk': 1})
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 200)

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('novaIdeja', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Ideja.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_form(self):  # <- new test
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_new_topic_invalid_post_data(self):  # <- updated this one
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)










