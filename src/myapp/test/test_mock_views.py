from django.test import TransactionTestCase
from rest_framework.reverse import reverse as rest_reverse
from .factories import AdminUserFactory
from myapp.models import Greeting


class FakeTestCase(TransactionTestCase):
    """ Should return the fake parameter as HTTP code
        /greetings/1?fake=300 should return the HTTP 300 code
    """

    fixtures = ['initial_data.json']
    multi_db = True

    def setUp(self):
        AdminUserFactory.create()
        self.client.login(username='admin', password='1234')

    def test_fake_argument_is_respected(self):
        test_status_code = 300

        # first test the standard

        response = self.client.get(rest_reverse('mock:greeting-detail',
                                                args=[1]), follow=True)

        self.assertNotEqual(response.status_code, test_status_code)

        response = self.client.get(rest_reverse('mock:greeting-detail',
                                                args=[1]) +
                                   '?fake=%s' % test_status_code,
                                   follow=True)

        self.assertEqual(response.status_code, test_status_code)

    def test_fake_argument_dont_do_the_action(self):
        test_status_code = 300

        before_count = Greeting.mock_objects.count()

        response = self.client.post(rest_reverse('mock:greeting-list') +
                                    '?fake=%s' % test_status_code,
                                    """
                                    {
                                        "name": "Toto"
                                    }
                                    """,
                                    content_type='application/json')

        self.assertEqual(response.status_code, test_status_code)
        self.assertEqual(Greeting.mock_objects.count(), before_count)


class MockTestCase(TransactionTestCase):
    fixtures = ['initial_data.json']
    multi_db = True
    reset_sequences = True

    def setUp(self):
        AdminUserFactory.create()
        self.client.login(username='admin', password='1234')

    def test_get_greetings(self):
        self.assertEqual(Greeting.mock_objects.count(), 2)

        response = self.client.get(rest_reverse('mock:greeting-list'),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

        # as order matter, do the order before the check
        id_values = list(Greeting.mock_objects.all())
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

        self.assertEqual(Greeting.mock_objects.count(), 2)

    def test_get_greeting_1(self):
        response = self.client.get(rest_reverse('mock:greeting-detail',
                                                args=[1]),
                                   follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": 1,
                                 "name": "Name1"
                             }
                             """)

    def test_post_greeting(self):
        before_count = Greeting.mock_objects.count()

        response = self.client.post(rest_reverse('mock:greeting-list'),
                                    """
                                    {
                                        "name": "Toto"
                                    }
                                    """,
                                    content_type='application/json',
                                    follow=True)

        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": 3,
                                 "name": "Toto"
                             }
                             """)

        # yes, since it's the mock service, the response is as if something was
        # created, but the DB is as before
        self.assertEqual(Greeting.mock_objects.count(), before_count)
        with self.assertRaises(Greeting.DoesNotExist):
            Greeting.mock_objects.get(name='Toto')

    def test_put_greeting(self):
        before_count = Greeting.mock_objects.count()

        response = self.client.put(rest_reverse('mock:greeting-detail',
                                                args=[1]),
                                   """
                                   {
                                       "name": "newName"
                                   }
                                   """,
                                   content_type='application/json',
                                   follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content,
                             """
                             {
                                 "id": 1,
                                 "name": "newName"
                             }
                             """)

        # no new object in the 'mock' db
        self.assertEqual(Greeting.mock_objects.count(), before_count)

        self.assertNotEqual(Greeting.mock_objects.get(pk=1).name, 'newName')

    def test_delete_greeting(self):
        self.assertTrue(Greeting.mock_objects.get(id=1))

        response = self.client.delete(rest_reverse('mock:greeting-detail',
                                                   args=[1]),
                                      follow=True)

        self.assertEqual(response.status_code, 204)

        # and the object still exists in the 'mock' db (rollbacked)
        self.assertTrue(Greeting.mock_objects.get(id=1))
