from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post


class PostViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='pass',
            phone_number = '+71234567890'
        )
        self.other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='pass',
            phone_number='+70987654321'
        )

        for i in range(3):
            Post.objects.create(
                owner=self.user,
                title=f"Title {i}",
                content="content",
                created_at=f"2025-01-0{i + 1}"
            )

        self.free_post = Post.objects.create(
            owner=self.user,
            title='Free Post',
            content='...',
            price_type='free'
        )
        self.paid_post = Post.objects.create(
            owner=self.user,
            title='Paid Post',
            content='...',
            price_type='paid'
        )

        self.test_post = Post.objects.create(
            owner=self.user,
            title='Post Title',
            content='content'
        )


    def test_home_view_authenticated_user(self):
        self.client.login(phone_number='+71234567890', password='pass')
        url = reverse('posts:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_user'], self.user)
        self.assertEqual(response.context['user_post_count'], 6)

    def test_user_posts_view_anonymous(self):
        url = reverse('posts:user_posts', kwargs={'username': 'testuser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    def test_user_posts_view_authenticated_owner(self):
        self.client.login(phone_number='+71234567890', password='pass')
        url = reverse('posts:user_posts', kwargs={'username': 'testuser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)
        self.assertEqual(response.context['is_owner'], True)

    def test_user_posts_view_not_owner(self):
        self.client.login(phone_number='+70987654321', password='pass')
        url = reverse('posts:user_posts', kwargs={'username': 'testuser'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view(self):
        url = reverse('posts:post_detail', kwargs={'pk': self.test_post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.test_post)
        self.assertIn('title', response.context)
        self.assertContains(response, 'Post Title')

    def test_post_create_view_redirects_when_not_authenticated(self):
        url = reverse('posts:create_post')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # редирект на login

    def test_post_create_view_creates_post(self):
        self.client.login(phone_number='+71234567890', password='pass')
        url = reverse('posts:create_post')
        data = {
            'title': 'New Post',
            'content': 'Content of post',
            'price_type': 'free',
            'price': 0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        new_post = Post.objects.filter(title='New Post').first()
        self.assertIsNotNone(new_post)
        self.assertEqual(new_post.owner, self.user)

    def test_update_view_owner(self):
        self.client.login(phone_number='+71234567890', password='pass')
        url = reverse('posts:post_edit', kwargs={'pk': self.test_post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_post = self.client.post(url, {'title': 'Updated', 'content': '...', 'price_type': 'free',' price': 0})
        self.assertEqual(response_post.status_code, 302)
        self.test_post.refresh_from_db()
        self.assertEqual(self.test_post.title, 'Updated')

    def test_update_view_non_owner(self):
        self.client.login(phone_number='+70987654321', password='pass')
        response = self.client.get(reverse("posts:post_edit", kwargs={"pk": self.test_post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("posts:post_detail", kwargs={"pk": self.test_post.pk}))
