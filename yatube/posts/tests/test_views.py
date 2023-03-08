from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.forms import PostForm
from posts.models import Group, Post
from django.urls import reverse


User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
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
        cls.user_other = User.objects.create(username='OtherName')
        cls.group_other = Group.objects.create(
            title='Тестовое название группы',
            slug='test-other-slug',
            description='Тестовое описание 2'
        )

        cls.URL_INDEX = reverse('posts:index')
        cls.URL_POST_CREATE = reverse('posts:post_create')
        cls.URL_GROUP = reverse('posts:group_list', args=(cls.group.slug,))
        cls.URL_PROFILE = reverse('posts:profile', args=(cls.user,))
        cls.URL_POST_DETAIL = reverse('posts:post_detail', args=(cls.post.pk,))
        cls.URL_POST_EDIT = reverse('posts:post_edit', args=(cls.post.pk,))

        cls.templates_page_names = {
            cls.URL_GROUP: 'posts/group_list.html',
            cls.URL_PROFILE: 'posts/profile.html',
            cls.URL_POST_DETAIL: 'posts/post_detail.html',
            cls.URL_POST_EDIT: 'posts/create_post.html',
            cls.URL_POST_CREATE: 'posts/create_post.html',
            reverse('users:signup'): 'users/signup.html',
            '/auth/login/?next=/create/': 'users/login.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(self.user_other)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(
                    response, template,
                    f'''Страница {url} для шаблона {template} не найдена'''
                )

    def test_page_show_correct_context(self):
        """Шаблон с правильным контекстом."""
        url_code = {self.URL_INDEX, self.URL_GROUP,
                    self.URL_PROFILE, self.URL_POST_DETAIL}
        for url in url_code:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if url == self.URL_POST_DETAIL:
                    first_object = response.context.get('post')
                else:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    first_object = response.context.get('page_obj')[0]
                self.assertEqual(first_object.pk, self.post.pk)
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(first_object.author, self.post.author)
                self.assertEqual(first_object.group.slug, self.group.slug)
                self.assertEqual(first_object.group.title, self.group.title)
                self.assertEqual(first_object.group.description,
                                 self.group.description)

    def test_posts_page_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        urls = {self.URL_POST_CREATE, self.URL_POST_EDIT}
        for url in urls:
            response = self.authorized_client.get(url)
            form_fields = {'text', 'group', 'is_edit'}
            for value in form_fields:
                with self.subTest(value=value):
                    form_field = response.context.get('form')
                    self.assertIsInstance(form_field, PostForm)
