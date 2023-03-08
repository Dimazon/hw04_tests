from http import HTTPStatus as H
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
        cls.user_other = User.objects.create(username='OtherName')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
        )

        cls.HOME_URL = '/'
        cls.GROUP_URL = f'/group/{cls.post.group.slug}/'
        cls.PROFILE_URL = f'/profile/{cls.user.username}/'
        cls.POST_DETAIL_URL = f'/posts/{cls.post.pk}/'
        cls.UNEXISTING_PAGE_URL = '/unexisting_page/'
        cls.POST_CREATE_URL = '/create/'
        cls.URL_REDIRECT_NOT_AUTHOR_POST = f'/posts/{cls.post.pk}/edit/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.user_other)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get(self.HOME_URL)
        self.assertEqual(response.status_code, H.OK)

    def test_group_url_exists_at_desired_location(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get(self.GROUP_URL)
        self.assertEqual(response.status_code, H.OK)

    def test_profile_url_exists_at_desired_location(self):
        """Страница /profile/<username>/ доступна
        авторизованному пользователю."""
        response = self.authorized_client.get(
            self.PROFILE_URL
        )
        self.assertEqual(response.status_code, H.OK)

    def test_post_detail_url_exists_at_desired_location_authorized(self):
        """Страница /posts/<post_id>/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(self.POST_DETAIL_URL)
        self.assertEqual(response.status_code, H.OK)

    def test_unexisting_page(self):
        """Неверно указанная страница /unexisting_page/ возвращает
        ошибку для всех пользователей."""
        response = self.guest_client.get(self.UNEXISTING_PAGE_URL)
        self.assertEqual(response.status_code, H.NOT_FOUND)

    def test_post_create_url_redirect_anonymous(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get(self.POST_CREATE_URL)
        self.assertEqual(response.status_code, H.FOUND)

    def test_url_redirect_not_author_post(self):
        """Страница /posts/<int:post_id>/edit/ перенаправляет всех,
        кроме автора поста."""
        response = self.authorized_client_other.get(
            self.URL_REDIRECT_NOT_AUTHOR_POST
        )
        self.assertEqual(response.status_code, H.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.post.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
            'posts/create_post.html': '/create/'
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
