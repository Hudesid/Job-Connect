from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class JobPostingListTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/job-postings/list/"

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobPostingCreateTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/job-postings/announce/"

    def test_list_get(self):
        data = {
            "title": "Test",
            "location": "test",
            "job_type": "Part time",
            "experience_level": "Entry",
            "salary_min": 100.00,
            "salary_max": 200.00,
            "deadline": timezone.now() + timedelta(days=7),
            "requirements": "test",
            "responsibilities": "test",
            "education_required": "Masters",
            "skills_required": 1
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobPostingRetrieveTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/job-postings/detail/1/"

    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobPostingRetrieveUpdateDestroyTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/job-postings/my-post/1/"

    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_patch(self):
        data = {"salary_max": 250.00}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_delete(self):
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobPostingRecommendedTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/job-postings/recommended/"
        self.client = APIClient()

    def test_recommended_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobApplicationListCreateTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/applications/"
        self.client = APIClient()

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        data = {"job_posting": 1, "cover_later": "test", "resume": "something docs or pdf file."}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class JobApplicationRetrieveTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/applications/detail/1/"
        self.client = APIClient()

    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobApplicationRetrieveUpdateDestroyTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/applications/my-application/1/"
        self.client = APIClient()

    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_patch(self):
        data = {"job_posting": 2}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_delete(self):
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobApplicationUpdateTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/applications/1/status/"
        self.client = APIClient()

    def test_update_patch(self):
        data = {"status": "Rejected"}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobPostingApplicationListTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/job-postings/1/applications/"
        self.client = APIClient()

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SavedJobListTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/saved-jobs/"
        self.client = APIClient()

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_post(self):
        data = {"job_posting": 1}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SavedJobDestroyTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/saved-jobs/delete/1/"
        self.client = APIClient()

    def test_destroy_delete(self):
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobPostingStatsListTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/stats/job-postings/"
        self.client = APIClient()

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JobApplicationStatsListTestCase(APITestCase):
    def setUp(self):
        self.url = "/api/stats/applications/"
        self.client = APIClient()

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
