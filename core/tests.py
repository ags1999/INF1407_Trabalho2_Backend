from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Livro

User = get_user_model()


class AuthTests(APITestCase):
    """Testa cadastro, login e proteção de endpoints."""

    def test_endpoint_protegido_exige_login(self):
        resp = self.client.get(reverse('livro-list'))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_retorna_token(self):
        user = User.objects.create_user(
            email='ana@example.com', username='ana', password='SenhaForte123'
        )
        user.is_active = True
        user.save()
        resp = self.client.post(
            reverse('login'),
            {'email': 'ana@example.com', 'password': 'SenhaForte123'},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)


class LivroCrudTests(APITestCase):
    """Testa o CRUD de livros e o isolamento entre usuários."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='bob@example.com', username='bob', password='SenhaForte123', is_active=True
        )
        self.other = User.objects.create_user(
            email='eve@example.com', username='eve', password='SenhaForte123', is_active=True
        )
        self.client.force_authenticate(self.user)

    def test_criar_e_listar_livro(self):
        resp = self.client.post(reverse('livro-list'), {
            'google_volume_id': 'abc123',
            'title': 'Dom Casmurro',
            'author': 'Machado de Assis',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.get(reverse('livro-list'))
        self.assertEqual(len(resp.data), 1)

    def test_usuario_nao_ve_livro_de_outro(self):
        Livro.objects.create(
            user=self.other, google_volume_id='x', title='Outro', author='Alguém'
        )
        resp = self.client.get(reverse('livro-list'))
        self.assertEqual(len(resp.data), 0)

    def test_atualizar_anotacoes(self):
        livro = Livro.objects.create(
            user=self.user, google_volume_id='y', title='Livro', author='Autor'
        )
        resp = self.client.patch(
            reverse('livro-detail', args=[livro.pk]),
            {'user_notes': 'Adorei!'},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        livro.refresh_from_db()
        self.assertEqual(livro.user_notes, 'Adorei!')

    def test_remover_livro(self):
        livro = Livro.objects.create(
            user=self.user, google_volume_id='z', title='Livro', author='Autor'
        )
        resp = self.client.delete(reverse('livro-detail', args=[livro.pk]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Livro.objects.count(), 0)
