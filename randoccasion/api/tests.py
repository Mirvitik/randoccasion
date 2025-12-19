__all__ = ()

from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework_api_key.models import APIKey


class TestAPI(TestCase):
    fixtures = ["fixtures/data.json"]

    def setUp(self):
        _, self.key = APIKey.objects.create_key(name="test-key")
        self.client = Client(headers={"authorization": f"Api-Key {self.key}"})

    def test_list(self):
        response = self.client.get(reverse("api:user-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(
            {
                "id": 1,
                "username": "user1",
                "first_name": "",
                "last_name": "",
                "email": "user@example.com",
            },
            response.json(),
        )
        self.assertIn(
            {
                "id": 2,
                "username": "user2",
                "first_name": "",
                "last_name": "",
                "email": "user2@example.com",
            },
            response.json(),
        )

    def test_get_user_by_id(self):
        response = self.client.get(
            reverse("api:user-detail", kwargs={"pk": "1"}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            {
                "id": 1,
                "username": "user1",
                "first_name": "",
                "last_name": "",
                "email": "user@example.com",
            },
            response.json(),
        )

    def test_events_list(self):
        response = self.client.get(reverse("api:event-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_event_by_id(self):
        response = self.client.get(
            reverse("api:event-detail", kwargs={"pk": "1"}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_event(self):
        data = {
            "name": "test event",
            "slug": "test-event",
        }
        response = self.client.post(reverse("api:interest-list"), data=data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_interests_list(self):
        response = self.client.get(reverse("api:interest-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(
            {"id": 1, "name": "music", "slug": "music"},
            response.json(),
        )

    def test_interest_by_id(self):
        response = self.client.get(
            reverse("api:interest-detail", kwargs={"pk": "1"}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            {"id": 1, "name": "music", "slug": "music"},
            response.json(),
        )

    def test_create_interest(self):
        data = {
            "name": "test interest",
            "slug": "test-interest",
        }
        response = self.client.post(reverse("api:interest-list"), data=data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertIn(
            '"name":"test interest","slug":"test-interest"}',
            response.content.decode("UTF-8"),
        )

    def test_login(self):
        data = {
            "username": "user1",
            "password": "fpuWIOYT#WUEY2",
        }
        response = self.client.post(reverse("api:login"), data=data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            (
                '{"message":"Успешный вход","user_id":1,"username":"user1",'
                '"email":"user@example.com","first_name":"","last_name":""}'
            ),
            response.content.decode("UTF-8"),
        )
