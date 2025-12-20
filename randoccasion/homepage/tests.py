__all__ = ()

from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class TestHomepage(TestCase):
    def test_index(self):
        response = Client().get(reverse("homepage:main"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_privacy(self):
        response = Client().get(reverse("homepage:privacy"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
