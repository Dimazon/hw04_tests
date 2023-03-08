from http import HTTPStatus as H
from django.test import TestCase, Client


class StaticTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_url_exists_at_desired_location(self):
        """Страница доступна всем."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, H.OK)

    def test_about_tech_url_exists_at_desired_location(self):
        """Страница доступна всем."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, H.OK)

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_about_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_about_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
