from django.core.exceptions import ValidationError
from django.test import TransactionTestCase
from .factories import GreetingFactory
from myapp.models import Greeting


class GreetingsTestCase(TransactionTestCase):
    def setUp(self):
        # fixtures
        (self.mpl, self.mi) = GreetingFactory.create_batch(2)

    def test_unicode_representation(self):
        self.assertEqual(str(self.mpl), 'Name1')

    def test_greeting_creation(self):
        GreetingFactory(name='This is a test')

        self.assertEqual(
            len(Greeting.objects.filter(name='This is a test')), 1)

    def test_missing_name(self):
        with self.assertRaises(Exception):
            GreetingFactory(name=None)

    def test_blank_name(self):
        with self.assertRaises(ValidationError):
            GreetingFactory.build(name='').full_clean()
