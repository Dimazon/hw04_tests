from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post
from django.urls import reverse
from posts.views import NUM_OF_POSTS


User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.NUM_OF_POSTS_CREATE = NUM_OF_POSTS
        cls.PAGINATE_BY: int = 10

        cls.author = User.objects.create_user(username="author")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание'
        )

        cls.list_url_reverse_template = {
            'INDEX': reverse('posts:index'),
            'GROUP_LIST': reverse(
                'posts:group_list', kwargs={'slug': 'slug-test'}
            ),
            'PROFILE': reverse(
                'posts:profile', kwargs={'username': f'{cls.author}'}
            ),
        }

        cls.post = [
            Post.object.bulk_create(
                [
                    Post(
                        text=f'text_post_{_}',
                        author=cls.author,
                        group=cls.group
                    )
                    for _ in range(cls.NUM_OF_POSTS_CREATE)
                ]
            )
        ]
