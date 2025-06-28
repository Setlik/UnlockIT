from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from users.models import User, AuthorSubscription
from users.views import verification_codes, registration_sessions


class UserViewTests(TestCase):
    def setUp(self):
        User.objects.all().delete()
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass', email='test@example.com',
                                             phone_number='+71111111111')
        self.author = User.objects.create_user(username='author', password='pass', email='author@example.com',
                                               phone_number='+72222222222')

    @patch('users.views.send_verification_code')
    def test_register_post_success(self, mock_send_code):
        mock_send_code.return_value = 123456
        data = {
            'username': 'testuser2',
            'phone_number': '+72345678900',
            'email': 'test@example.com',
            'password': 'newpass',
            'password_confirm': 'newpass',
        }
        response = self.client.post(reverse('users:register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:confirm_code', args=['+72345678900']))
        print(response.content)

    def test_confirm_code_success(self):
        phone = '+72345678900'
        verification_codes[phone] = '123456'
        registration_sessions[phone] = {
            'password': 'pass',
            'username': 'testuser2',
            'email': 'test@example.com'
        }
        response = self.client.post(reverse('users:confirm_code', args=[phone]), {'code': '123456'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:login'))
        self.assertTrue(User.objects.filter(phone_number=phone).exists())

    def test_login_view_success(self):
        response = self.client.post(reverse('users:login'), {
            'username': '+71111111111',
            'password': 'pass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('posts:home'))

    def test_logout_view(self):
        self.client.login(username='testuser', password='pass')
        response = self.client.get(reverse('users:logout'))
        self.assertRedirects(response, reverse('posts:home'))

    @patch('stripe.Product.create')
    @patch('stripe.Price.create')
    @patch('stripe.checkout.Session.create')
    def test_subscription_payment(self, mock_session_create, mock_price_create, mock_product_create):
        mock_product_create.return_value = type('obj', (object,), {'id': 'prod_id'})()
        mock_price_create.return_value = type('obj', (object,), {'id': 'price_id'})()
        mock_session_create.return_value = type('obj', (object,), {'url': 'http://testsession'})()

        self.client.force_login(self.user)
        response = self.client.post(reverse('users:subscription_payment', args=[self.author.pk]))
        self.assertRedirects(response, 'http://testsession')

    def test_subscription_success(self):
        self.client.login(phone_number='+71111111111', password='pass')
        subscription = AuthorSubscription.objects.create(
            subscriber=self.user,
            author=self.author,
            amount=1000,
            session_id='sess_123',
            is_active=False
        )
        response = self.client.get(
            reverse('users:subscription_success', args=[self.author.pk]) + '?session_id=sess_123')
        self.assertEqual(response.status_code, 200)
        subscription.refresh_from_db()
        self.assertTrue(subscription.is_active)

    def test_subscription_cancel(self):
        response = self.client.get(reverse('users:subscription_cancel', args=[self.author.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscription/subscription_cancel.html')
