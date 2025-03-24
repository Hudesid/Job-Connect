from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class MyNotificationsListGetTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/notifications/my-notification/"
        self.client = APIClient()


    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NotificationsListGetTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/notifications/1/"
        self.client = APIClient()


    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NotificationPutTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/notifications/1/read/"
        self.client = APIClient()


    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NotificationsPutTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/notifications/read-all/"
        self.client = APIClient()


    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)