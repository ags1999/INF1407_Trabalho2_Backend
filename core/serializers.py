from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import Livro

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializa o cadastro de um novo usuário (com validação de senha)."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirmação de senha')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'As senhas não conferem.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        # Cria o usuário inativo até confirmar o e-mail
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Dados básicos do usuário (perfil)."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id', 'email')


class LivroSerializer(serializers.ModelSerializer):
    """Serializa os livros da estante do usuário."""

    class Meta:
        model = Livro
        fields = (
            'id', 'google_volume_id', 'title', 'author',
            'cover_url', 'user_notes', 'date_added',
        )
        read_only_fields = ('id', 'date_added')


class ChangePasswordSerializer(serializers.Serializer):
    """Troca de senha do usuário autenticado."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value


class GoogleBookSerializer(serializers.Serializer):
    """Resultado de busca vindo da API do Google Books (somente leitura)."""

    google_volume_id = serializers.CharField()
    title = serializers.CharField()
    author = serializers.CharField()
    cover_url = serializers.CharField(allow_blank=True)
