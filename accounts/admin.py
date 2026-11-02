from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CostumUserCreateForms, CostumUserChangeForms
from .models import CostumUser


@admin.register(CostumUser)
class CustomUserAdmin(UserAdmin):
    add_form = CostumUserCreateForms
    form = CostumUserChangeForms
    model = CostumUser

    list_display = ("email", "username", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")

    ordering = ("email",)
    search_fields = ("email", "username")

    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

