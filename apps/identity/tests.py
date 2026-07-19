from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, MemberProfile


class AuthTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='testadmin', password='TestPass123x', role=User.Role.ADMIN
        )
        self.member_user = User.objects.create_user(
            username='testmemberuser', password='TestPass123x', role=User.Role.MEMBER
        )
        MemberProfile.objects.create(user=self.member_user, member_code='MEM-TEST01')

    def test_login_returns_role(self):
        """Login response must include the role field, needed by mobile app to route screens."""
        response = self.client.post('/api/auth/login/', {
            'username': 'testadmin', 'password': 'TestPass123x'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
        self.assertIn('access', response.data)

    def test_login_wrong_password_fails(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'testadmin', 'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_register_member(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/members/', {
            'username': 'newmember', 'password': 'NewPass123x',
            'first_name': 'New', 'last_name': 'Member',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], 'member')
        self.assertTrue(response.data['member_code'].startswith('MEM-'))

    def test_member_cannot_register_member(self):
        """This is the exact 403 test we ran manually earlier via curl."""
        self.client.force_authenticate(user=self.member_user)
        response = self.client.post('/api/members/', {
            'username': 'anothernew', 'password': 'NewPass123x',
            'first_name': 'Another', 'last_name': 'One',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)