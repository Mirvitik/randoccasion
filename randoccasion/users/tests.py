__all__ = ()

from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from users.models import User


class TestUser(TestCase):
    fixtures = ["fixtures/data.json"]

    def setUp(self):
        self.client = Client()

    def test_index(self):
        response = self.client.get(reverse("homepage:main"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_privacy(self):
        response = self.client.get(reverse("homepage:privacy"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "user1", "password": "fpuWIOYT#WUEY2"},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(User.objects.get(pk=1), response.context["user"])
