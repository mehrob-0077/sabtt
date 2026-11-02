from django.contrib.auth.models import BaseUserManager

class CostumUserMeneger(BaseUserManager):
    def _create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError("Необходимо указать адрес электронной почты")
        email = self.normalize_email(email.strip()).lower()
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email,password,**extra_fields):
        extra_fields.setdefault('is_active',False)
        if extra_fields.get('is_staff') is True or extra_fields.get('is_superuser') is True:
            raise ValueError("Обычный пользователь не может быть сотрудником или суперпользователем")
        return self._create_user(email,password,**extra_fields)

    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("У суперпользователя должен быть is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("У суперпользователя должен быть is_superuser=True")
        if extra_fields.get('is_active') is not True:
            raise ValueError("У суперпользователя должен быть is_active=True")
        return self._create_user(email,password,**extra_fields)
        
        
