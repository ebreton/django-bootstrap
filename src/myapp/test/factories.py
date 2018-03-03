import factory
from django.contrib.auth import get_user_model


class AdminUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = 'admin'
    email = 'admin@localhost'
    password = factory.PostGenerationMethodCall('set_password', '1234')

    is_superuser = True
    is_staff = True
    is_active = True
