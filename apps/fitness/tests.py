from datetime import date
from rest_framework.test import APITestCase
from rest_framework import status
from apps.identity.models import User
from .models import Goal, TrainerAssignment


class TrainerIsolationTests(APITestCase):
    def setUp(self):
        self.member = User.objects.create_user(username='member1', password='pass123x', role=User.Role.MEMBER)
        self.trainer1 = User.objects.create_user(username='trainer1', password='pass123x', role=User.Role.TRAINER)
        self.trainer2 = User.objects.create_user(username='trainer2', password='pass123x', role=User.Role.TRAINER)

        TrainerAssignment.objects.create(member=self.member, trainer=self.trainer1, is_active=True)

        self.goal = Goal.objects.create(
            member=self.member, goal_type='weight_loss', target_date=date(2026, 12, 31)
        )

    def test_assigned_trainer_can_see_goal(self):
        self.client.force_authenticate(user=self.trainer1)
        response = self.client.get('/api/goals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unassigned_trainer_cannot_see_goal(self):
        """The exact gap caught during manual testing — must stay fixed."""
        self.client.force_authenticate(user=self.trainer2)
        response = self.client.get('/api/goals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_member_can_create_own_goal(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post('/api/goals/', {
            'goal_type': 'muscle_gain', 'target_date': '2026-12-31',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['member'], self.member.id)

    def test_unassigned_trainer_cannot_create_workout_plan(self):
        self.client.force_authenticate(user=self.trainer2)
        response = self.client.post('/api/workout-plans/', {
        'member': self.member.id, 'title': 'Sneaky Plan', 'exercises': [],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)