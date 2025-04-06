from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class SkillModelViewSetTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/skills/'
        self.client = APIClient()


    def test_create_post(self):
        data = {"name": "Pyton", "category": "Soft Skill"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_retrieve_get(self):
        response = self.client.get('/api/skills/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_update_patch(self):
        data = {"category": "Programming"}
        response = self.client.patch('/api/skills/1/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_destroy_delete(self):
        response = self.client.get('/api/skills/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
