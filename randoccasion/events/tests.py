__all__ = ()

from django.test import TestCase
from django.utils import timezone

from events.models import Event
from users.models import Interest, Profile, User


class RecommendedEventsTestCase(TestCase):
    def setUp(self):

        self.interest_music = Interest.objects.create(
            name="Музыка",
            slug=("Музыка"),
        )
        self.interest_sport = Interest.objects.create(
            name="Спорт",
            slug=("Спорт"),
        )
        self.user1 = User.objects.create_user(
            username="user1",
            password="pass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            password="pass123",
        )

        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)

        self.user1.profile.interests.add(self.interest_music)
        self.user2.profile.interests.add(self.interest_sport)

        self.event1 = Event.objects.create(
            name="Концерт",
            creator=self.user2,
            expires_at=timezone.now() + timezone.timedelta(hours=2),
            max_participants=5,
            slug="dd",
        )
        self.event1.interests.add(self.interest_music)

        self.event2 = Event.objects.create(
            name="Футбол",
            creator=self.user2,
            expires_at=timezone.now() + timezone.timedelta(hours=2),
            max_participants=5,
            slug="dww",
        )
        self.event2.interests.add(self.interest_sport)

        self.event3 = Event.objects.create(
            name="Йога",
            creator=self.user2,
            expires_at=timezone.now() + timezone.timedelta(hours=2),
            max_participants=1,
            slug="tyu",
        )
        self.event3.interests.add(self.interest_music)
        self.event3.participants.add(self.user1)

        self.event4 = Event.objects.create(
            name="Выставка",
            creator=self.user2,
            expires_at=timezone.now() - timezone.timedelta(hours=1),
            max_participants=5,
            is_active=True,
            slug="sdsd",
        )
        self.event4.interests.add(self.interest_music)

    def test_recommended_events_for_user(self):
        recommended = Event.objects.recommended_events_for_user(self.user1)
        self.assertIn(self.event1, recommended)
        self.assertNotIn(self.event2, recommended)
        self.assertNotIn(self.event3, recommended)
        self.assertNotIn(self.event4, recommended)

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
