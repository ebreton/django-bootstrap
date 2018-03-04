from django.test import TransactionTestCase
from rest_framework.reverse import reverse
from .factories import GreetingFactory, AdminUserFactory
from myapp.models import Greeting


class APITestCase(TransactionTestCase):
    # reset_sequences = True

    def setUp(self):
        # fixtures
        (self.mpl, self.mi) = GreetingFactory.create_batch(2)

        AdminUserFactory.create()
        self.client.login(username='admin', password='1234')

    def test_missing_name(self):
        as_before = Greeting.objects.count()

        response = self.client.post(reverse('api:greeting-list'),
                                    """
                                    {
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Greeting.objects.count(), as_before)

    def test_blank_name(self):
        as_before = Greeting.objects.count()

        response = self.client.post(reverse('api:greeting-list'),
                                    """
                                    {
                                        "name": "",
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Greeting.objects.count(), as_before)

    # - 1. GET /greetings
    def test_get_greetings(self):
        self.assertEqual(Greeting.objects.count(), 2)

        response = self.client.get(reverse('api:greeting-list'), follow=True)

        self.assertEqual(response.status_code, 200)
        # as order matter, do the order before the check
        id_values = (self.mpl, self.mi)
        id_values = sorted(id_values, key=lambda tup: tup.pk, reverse=True)

        self.assertJSONEqual(response.content,
                             """
                             {
                                 "count": 2,
                                 "next": null,
                                 "previous": null,
                                 "results": [
                                     {
                                        "id": %s,
                                        "name": "%s"
                                     },
                                     {
                                        "id": %s,
                                        "name": "%s"
                                     }
                                 ]
                             }
                             """ % (id_values[0].pk,
                                    id_values[0].name,
                                    id_values[1].pk,
                                    id_values[1].name)
                             )

        self.assertEqual(Greeting.objects.count(), 2)

    # - 2. GET /greetings/1
    def test_get_greeting_1(self):
        response = self.client.get(reverse('api:greeting-detail',
                                           args=[self.mpl.pk]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": %s,
                                 "name": "Name1"
                             }
                             """ % (self.mpl.pk,))

    def test_get_greeting_1_doesnt_exist(self):
        pk = self.mpl.pk

        self.mpl.delete()

        response = self.client.get(reverse('api:greeting-detail',
                                           args=[pk]),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_get_greeting_invalid_pk(self):
        response = self.client.get(reverse('api:greeting-detail',
                                           args=['invalid_pk']),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    # - 3. POST /greetings
    def test_post_greeting(self):
        before_count = Greeting.objects.count()

        response = self.client.post(reverse('api:greeting-list'),
                                    """
                                    {
                                        "name": "Toto"
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Greeting.objects.count(), before_count + 1)
        new_pk = Greeting.objects.get(name='Toto').pk

        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": %s,
                                 "name": "Toto"
                             }
                             """ % (new_pk,))

    def test_post_greeting_invalid_payload(self):
        response = self.client.post(reverse('api:greeting-list'),
                                    """
                                    {
                                        name: "Not a valid payload
                                        &/())== at all !!!!,, []
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("JSON parse error" in response.data.get('detail'))

    def test_post_greeting_invalid_name(self):
        name_max_length = Greeting._meta.get_field('name').max_length
        too_long = 'x' * (name_max_length + 1)

        response = self.client.post(reverse('api:greeting-list'),
                                    """
                                    {
                                        "name": "%s"
                                    }
                                    """ % (too_long,),
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("no more than %s characters" % (name_max_length,)
                        in str(response.data.get('name')))

    # - 4. PUT /greetings/1
    def test_put_greeting(self):
        before_count = Greeting.objects.count()

        pk = self.mpl.pk
        self.assertNotEqual(self.mpl.name, 'newName')

        response = self.client.put(reverse('api:greeting-detail',
                                           args=[pk]),
                                   """
                                   {
                                       "name": "newName"
                                   }
                                   """,
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Greeting.objects.count(), before_count)
        self.assertTrue(Greeting.objects.get(name='newName'))

        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": %s,
                                 "name": "newName"
                             }
                             """ % (pk,))

    def test_put_greeting_invalid_payload(self):
        response = self.client.put(reverse('api:greeting-detail',
                                           args=[self.mpl.pk]),
                                   """
                                   {
                                       name: "Not a valid payload
                                       &/())== at all !!!!,, []
                                   }
                                   """,
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("JSON parse error" in response.data.get('detail'))

    def test_put_greeting_invalid_pk(self):
        response = self.client.put(reverse('api:greeting-detail',
                                           args=['invalid_pk']),
                                   """
                                   {
                                       "name": "newName"
                                   }
                                   """,
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_put_greeting_invalid_name(self):
        name_max_length = Greeting._meta.get_field('name').max_length
        too_long = 'x' * (name_max_length + 1)

        response = self.client.put(reverse('api:greeting-detail',
                                           args=[self.mpl.pk]),
                                   """
                                   {
                                       "name": "%s"
                                   }
                                   """ % (too_long,),
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 400)
        self.assertTrue("no more than %s characters" % (name_max_length,)
                        in str(response.data.get('name')))

    # - 5. DELETE /greetings/1
    def test_delete_greeting(self):
        pk = self.mpl.pk

        response = self.client.delete(reverse('api:greeting-detail',
                                              args=[self.mpl.pk]),
                                      follow=True)

        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Greeting.DoesNotExist):
            Greeting.objects.get(id=pk)

    def test_delete_greeting_invalid_pk(self):
        before_count = Greeting.objects.count()

        response = self.client.delete(reverse('api:greeting-detail',
                                              args=['invalid_pk']),
                                      follow=True)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Greeting.objects.count(), before_count)
