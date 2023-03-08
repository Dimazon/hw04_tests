from http import HTTPStatus as H
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
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
        cls.form = PostForm()

    @classmethod
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_form(self):
        """Валидная форма создает запись в посте"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=(self.user,))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=self.group.pk))
        self.assertEqual(response.status_code, H.OK)

    def test_cant_create_existing_slug(self):
        """Редактирование поста"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=self.group.pk).exists())
        self.assertEqual(response.status_code, H.FOUND)
