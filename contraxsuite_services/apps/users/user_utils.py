from apps.users.models import User


def get_main_admin_user() -> User:
    return User.objects.get_by_natural_key('Administrator')
