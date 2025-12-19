__all__ = ()

from django.test import TestCase

from events.models import Event
from users.models import Interest, Profile, User


class RecommendedEventsTestCase(TestCase):
    fixtures = ["fixtures/data.json"]

    def setUp(self):
        self.interest_music = Interest.objects.get(pk=1)
        self.interest_sport = Interest.objects.get(pk=4)

        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)

        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile2 = Profile.objects.get(user=self.user2)

        self.event1 = Event.objects.get(pk=1)
        self.event2 = Event.objects.get(pk=2)
        self.event3 = Event.objects.get(pk=3)
        self.event4 = Event.objects.get(pk=4)

    def test_recommended_events_for_user(self):
        recommended = Event.objects.recommended_events_for_user(self.user1)
        self.assertIn(self.event1, recommended)
        self.assertNotIn(self.event2, recommended)
        self.assertNotIn(self.event3, recommended)
        self.assertIn(self.event4, recommended)

    def test_no_interests_user(self):
        user_no_interest = User.objects.create_user(
            username="user3",
            password="pass123",
        )
        Profile.objects.create(user=user_no_interest)
        recommended = Event.objects.recommended_events_for_user(
            user_no_interest,
        )
        self.assertQuerySetEqual(recommended, [])
