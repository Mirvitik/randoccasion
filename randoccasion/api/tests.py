__all__ = ()

from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework_api_key.models import APIKey


class TestAPI(TestCase):
    fixtures = ["fixtures/data.json"]

    def setUp(self):
        _, self.key = APIKey.objects.create_key(name="test-key")
        self.client = Client(headers={"Authorization": f"Api-Key {self.key}"})
        self.token = self.client.post(
            reverse("api:login"),
            {"username": "user1", "password": "fpuWIOYT#WUEY2"},
        ).json()["token"]
        self.client_login = Client(
            headers={"Authorization": f"Token {self.token}"},
        )

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

    def test_deny_post_events(self):
        response = self.client.post(reverse("api:event-list"))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_access_login(self):
        response = self.client_login.post(
            reverse("api:event-list"),
            {"slug": "random-slug"},
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
