from django.test import TransactionTestCase
from django.urls import reverse
from .factories import GreetingFactory
from ..models import Greeting


class GreetingTest(TransactionTestCase):
    def setUp(self):
        self.mpl = GreetingFactory()

    def test_factory_create(self):
        """
        Test that we can create an instance via our object factory.
        """
        self.assertTrue(isinstance(self.mpl, Greeting))

    def test_list_view(self):
        """
        Test that the list view returns at least our factory created instance.
        """
        response = self.client.get(reverse('crud:greeting-list'))
        object_list = response.context['object_list']
        self.assertIn(self.mpl, object_list)

    def test_create_view(self):
        """
        Test that we can create an instance via the create view.
        """
        new_name = 'Name1'
        total = Greeting.objects.count()

        response = self.client.post(reverse('crud:greeting-create'),
                                    data={'name': new_name}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(total + 1, Greeting.objects.count())
        self.assertTrue(Greeting.objects.filter(name=new_name).exists())

    def test_detail_view(self):
        """
        Test that we can view an instance via the detail view.
        """
        response = self.client.get(self.mpl.get_absolute_url())
        self.assertEqual(response.context['object'], self.mpl)

    def test_update_view(self):
        """
        Test that we can update an instance via the update view.
        """
        update_name = 'greeting_updated'
        pk = self.mpl.pk

        with self.assertRaises(Greeting.DoesNotExist):
            Greeting.objects.get(name=update_name)

        response = self.client.post(reverse('crud:greeting-update',
                                            kwargs={'pk': pk, }),
                                    data={'name': update_name},
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Greeting.objects.get(name=update_name))

    def test_delete_view(self):
        """
        Test that we can delete an instance via the delete view.
        """
        pk = self.mpl.pk
        response = self.client.post(reverse('crud:greeting-delete',
                                            kwargs={'pk': pk, }),
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Greeting.objects.filter(pk=pk).exists())
