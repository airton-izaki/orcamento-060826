from django.db import models
from django.contrib.auth.models     import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Gerenciador customizado para criar usuários e superusuários."""
    def create_user(self, email, nome, password = None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório.')
        
        email = self.normalize_email(email)
        user = self.model(email = email,  nome = nome,  **extra_fields)
        user.set_password(password)
        user.save(using = self._db)

        return user

    def create_superuser(self, email, nome, password = None, **extra_fields):
        extra_fields.setdefault( 'is_staff', True )
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email,  nome,  password,  **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField( 
        verbose_name    = 'Nome Completo',
        max_length      = 150
    )
    email = models.EmailField(
        verbose_name    = 'E-mail',
        unique          = True
    )
    cpf = models.CharField(
        verbose_name    = 'CPF',
        max_length      = 11,
        unique          = True,
        blank           = True,
        null            = True
    )
    data_nascimento = models.DateField(
        verbose_name    = 'Data de Nascimento',
        blank           = True,
        null            = True,
    )
    telefone = models.CharField(
        verbose_name    = 'Telefone',
        max_length      = 11,
        blank           = True,
        null            = True,
    )

   # Controle de Acesso / Admin
    is_active = models.BooleanField(
        default         = True
    )
    is_staff = models.BooleanField(
        default = False
    )
    criado_em = models.DateTimeField(
        auto_now_add = True
    )

    objects = UserManager()

    # Define o email como campo principal de login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuario'

    def __str__(self):
        return f"{self.nome} ({self.email})"







