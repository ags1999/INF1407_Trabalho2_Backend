from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Livro
from core.serializers import (
    ChangePasswordSerializer,
    GoogleBookSerializer,
    LivroSerializer,
    RegisterSerializer,
    UserSerializer,
)
from core.services import GoogleBooksError, buscar_livros

User = get_user_model()


# ---------------------------------------------------------------------------
# Cadastro e ativação de conta
# ---------------------------------------------------------------------------
class RegisterView(generics.CreateAPIView):
    """Cadastra um novo usuário (inativo) e envia e-mail de ativação."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        from django.conf import settings

        user = serializer.save()
        # Monta o link de ativação apontando para o FRONTEND
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = f"{settings.FRONTEND_URL}/activate.html?uid={uid}&token={token}"
        send_mail(
            subject='Ative sua conta - Minha Estante',
            message=(
                f'Olá {user.username},\n\n'
                f'Confirme seu cadastro acessando o link abaixo:\n{link}\n\n'
                'Se você não solicitou este cadastro, ignore este e-mail.'
            ),
            from_email=None,
            recipient_list=[user.email],
        )


class ActivateAccountView(APIView):
    """Confirma o e-mail e ativa a conta a partir de uid + token."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter('uid', str, description='UID codificado em base64'),
            OpenApiParameter('token', str, description='Token de ativação'),
        ]
    )
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'detail': 'Conta ativada com sucesso.'})
        return Response(
            {'detail': 'Link de ativação inválido ou expirado.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ---------------------------------------------------------------------------
# CRUD de livros (endpoint protegido)
# ---------------------------------------------------------------------------
class LivroViewSet(viewsets.ModelViewSet):
    """
    CRUD completo dos livros da estante.

    - GET    /api/livros/        -> lista os livros DO usuário logado
    - POST   /api/livros/        -> adiciona um livro à estante
    - GET    /api/livros/{id}/   -> detalhe de um livro
    - PUT    /api/livros/{id}/   -> atualiza (ex.: anotações)
    - PATCH  /api/livros/{id}/   -> atualização parcial
    - DELETE /api/livros/{id}/   -> remove o livro

    Endpoint protegido: exige autenticação. Cada usuário só acessa os
    próprios livros, garantindo visões diferentes por usuário.
    """

    serializer_class = LivroSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra pelo usuário logado: cada um vê apenas a própria estante
        return Livro.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # CREATE com tratamento de duplicata (constraint usuário + volume).
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        gid = serializer.validated_data.get('google_volume_id')
        if Livro.objects.filter(user=request.user, google_volume_id=gid).exists():
            return Response(
                {'detail': 'Este livro já está na sua estante.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------------------------
# Busca de livros no Google Books (endpoint protegido)
# ---------------------------------------------------------------------------
class BookSearchView(APIView):
    """Busca livros na API do Google Books a partir de um termo (?q=)."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter('q', str, description='Termo de busca')],
        responses=GoogleBookSerializer(many=True),
    )
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([])
        try:
            resultados = buscar_livros(query)
        except GoogleBooksError as exc:
            return Response(
                {'detail': str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(GoogleBookSerializer(resultados, many=True).data)


# ---------------------------------------------------------------------------
# Perfil e gerência de senha
# ---------------------------------------------------------------------------
class ProfileView(generics.RetrieveUpdateAPIView):
    """Retorna e atualiza os dados do usuário autenticado (ex.: username)."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Troca a senha do usuário autenticado."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer, responses={200: None})
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Senha alterada com sucesso.'})


class PasswordResetRequestView(APIView):
    """Inicia a recuperação de senha enviando um link por e-mail."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {'email': {'type': 'string'}}}},
        responses={200: None},
    )
    def post(self, request):
        from django.conf import settings

        email = request.data.get('email', '')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = (
                f"{settings.FRONTEND_URL}/password-reset-confirm.html"
                f"?uid={uid}&token={token}"
            )
            send_mail(
                subject='Recuperação de senha - Minha Estante',
                message=(
                    f'Olá {user.username},\n\n'
                    f'Para redefinir sua senha, acesse:\n{link}\n\n'
                    'Se você não solicitou, ignore este e-mail.'
                ),
                from_email=None,
                recipient_list=[user.email],
            )
        except User.DoesNotExist:
            # Não revela se o e-mail existe (evita enumeração de usuários)
            pass
        return Response({
            'detail': 'Se o e-mail estiver cadastrado, você receberá as '
                      'instruções para redefinir a senha.'
        })


class PasswordResetConfirmView(APIView):
    """Confirma a redefinição de senha a partir de uid + token."""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request={'application/json': {'type': 'object', 'properties': {
            'uid': {'type': 'string'},
            'token': {'type': 'string'},
            'new_password': {'type': 'string'},
        }}},
        responses={200: None},
    )
    def post(self, request):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password', '')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'Link inválido ou expirado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            return Response({'new_password': exc.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Senha redefinida com sucesso.'})
