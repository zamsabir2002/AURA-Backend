from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth import get_user_model

# Create your models here.

class Role(models.Model):
    #username = models.CharField(max_length=50)
    id = models.PositiveIntegerField(primary_key=True)
    roles = models.CharField(max_length=50)
    def __str__(self):
        return self.roles

#User Manager Model
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, pass2=None,**extra_fields):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, name, password=None,**extra_fields):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.role = 1
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('role', 1)

        if extra_fields.get('role') != 1:
            raise ValueError('Does not have role of Admin')
        user.save(using=self._db)
        return user
#User Model
class User(AbstractBaseUser):
    # These fields tie to the roles!
    ADMIN = 1
    Risk_Analyser = 2
    Risk_Monitor = 3

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (Risk_Analyser, 'Risk Analyser'),
        (Risk_Monitor, 'Risk Monitor')
    )
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users', default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name","role"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.role
    @property
    def is_superuser(self):
        return self.is_admin

User = get_user_model()
class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50) 
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.email} - {self.activity_type} at {self.timestamp}'