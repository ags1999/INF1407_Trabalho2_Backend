from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    """Gerenciador de usuários que usa o e-mail como identificador principal."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O campo e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Usuário customizado: faz login com e-mail em vez de username."""

    email = models.EmailField('e-mail', unique=True)

    # Define o e-mail como o identificador usado no login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    # Renomeia os acessores reversos para evitar conflito com o User padrão
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_groups',
        blank=True,
        help_text='Os grupos aos quais este usuário pertence.',
        verbose_name='grupos',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions',
        blank=True,
        help_text='Permissões específicas deste usuário.',
        verbose_name='permissões',
    )

    def __str__(self):
        return self.email


class Livro(models.Model):
    """
    Livro salvo na estante pessoal de um usuário.

    Cada usuário só enxerga e manipula os próprios livros (visões diferentes
    por usuário). A combinação usuário + id do volume no Google Books é única,
    evitando duplicatas na mesma estante.
    """

    google_volume_id = models.CharField('ID do volume (Google Books)', max_length=255, default='')
    title = models.CharField('título', max_length=255)
    author = models.CharField('autor', max_length=255)
    cover_url = models.URLField('capa', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='livros', verbose_name='usuário')
    date_added = models.DateTimeField('adicionado em', auto_now_add=True)
    user_notes = models.CharField('anotações', max_length=255, blank=True)

    class Meta:
        verbose_name = 'livro'
        verbose_name_plural = 'livros'
        ordering = ['-date_added']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'google_volume_id'],
                name='unique_user_book',
            )
        ]

    def __str__(self):
        return self.title
