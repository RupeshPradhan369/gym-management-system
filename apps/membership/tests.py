from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from apps.identity.models import User
from .models import MembershipPlan, Membership


class MembershipTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass123x', role=User.Role.ADMIN)
        self.member = User.objects.create_user(username='member1', password='pass123x', role=User.Role.MEMBER)
        self.plan = MembershipPlan.objects.create(
            name='Monthly', duration_value=1, duration_unit=MembershipPlan.DurationUnit.MONTHS, price='2000.00'
        )

    def test_create_membership_computes_end_date(self):
        """The exact bug fixed in the original session — end_date must be server-computed."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/memberships/', {
            'member': self.member.id, 'plan': self.plan.id, 'start_date': '2026-01-15',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['end_date'], '2026-02-15')
        self.assertEqual(response.data['status'], 'active')

    def test_freeze_then_unfreeze_preserves_zero_day_end_date(self):
        membership = Membership.objects.create(
            member=self.member, plan=self.plan, start_date=date(2026, 1, 15), end_date=date(2026, 2, 15)
        )
        self.client.force_authenticate(user=self.admin)

        freeze_response = self.client.post(f'/api/memberships/{membership.id}/freeze/', {'reason': 'test'})
        self.assertEqual(freeze_response.data['status'], 'frozen')
        self.assertEqual(len(freeze_response.data['freezes']), 1)

        unfreeze_response = self.client.post(f'/api/memberships/{membership.id}/unfreeze/')
        self.assertEqual(unfreeze_response.data['status'], 'active')
        # Same-day freeze/unfreeze = 0 frozen days = end_date unchanged
        self.assertEqual(unfreeze_response.data['end_date'], '2026-02-15')

    def test_member_cannot_create_membership(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post('/api/memberships/', {
            'member': self.member.id, 'plan': self.plan.id, 'start_date': '2026-01-15',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)