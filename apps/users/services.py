from django.db import transaction

from apps.users.models import User


def create_user_account(email: str, password: str, role: str, **extra_fields) -> User:
    """Create a new user account with email, password and role.

    Normalizes email to lowercase and wraps creation in an atomic transaction
    so that related operations (e.g. profile creation) can be added safely.
    """
    email = email.lower()
    with transaction.atomic():
        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            **extra_fields,
        )
        return user
