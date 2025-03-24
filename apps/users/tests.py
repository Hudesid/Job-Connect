from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class RegisterTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/auth/register/'
        self.client = APIClient()


    def test_register_post(self):
        data = {"username": "Test", "email": "test@gmail.com", "password": "132546587", "user_type": "job_seeker"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/auth/login/'
        self.client = APIClient()

    def test_login_post(self):
        data = {"email": "test@gmail.com", "password": "132546587"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RefreshTokenTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/auth/refresh/'
        self.client = APIClient()

    def test_refresh_post(self):
        data = {"refresh": "your refresh token"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LogoutTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/auth/logout/'
        self.client = APIClient()

    def test_logout_post(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class VerifyEmailTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/user/verify-email/1/sdafasrfwea/'
        self.client = APIClient()

    def test_verify_email_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ForgotPasswordTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/user/forgot-password/'
        self.client = APIClient()


    def test_forgot_password_post(self):
        data = {"email": "test@gmail.com"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RecoveryPasswordTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/user/recovery-password/1/fdsggfgss/'
        self.client = APIClient()


    def test_verify_token_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_recovery_password_post(self):
        data = {"password": "213243545"}
        response = self.client.post(self.url, data, fromat='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileRetrieveUpdateDestroyTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/user/me/'
        self.client = APIClient()

    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_update_patch(self):
        data = {"job_seeker": "employer"}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_destroy_delete(self):
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileRetrieveTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/user/profile/1/'
        self.client = APIClient()

    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileCreateTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/job-seeker/create/'
        self.client = APIClient()


    def test_create_post(self):
        data = {"first_name": "Test", "last_name": "test", "date_of_birth": "2007-03-02", "phone_number": "+998...", "location": "Tashkent", "bio": "test", "skills": 1, "experience_years": 2, "education_level": "test"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class CompanyCreateTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/companies/create/'
        self.client = APIClient()


    def test_create_post(self):
        data = {"name": "Test", "description": "test", "website": "your company url", "industry": "test", "location": "Tashkent", "founded_year": 1, "employees_count": 100}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CompanyListTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/companies/list/'
        self.client = APIClient()

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyRetrieveTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/companies/detail/1/'
        self.client = APIClient()

    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CompanyRetrieveUpdateDestroyTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/companies/my-company/1/'
        self.client = APIClient()


    def test_retrieve_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_update_patch(self):
        data = {"location": "Andijon"}
        response = self.client.patch(self.url, data, fromat='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_destroy_delete(self):
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ResumeUploadingTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/job-seeker/1/upload-resume/'
        self.client = APIClient()


    def test_uploading_post(self):
        data = {"resume": "your resume"}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UsersStatsListTestCase(APITestCase):
    def setUp(self):
        self.url = '/api/stats/users/'
        self.client = APIClient()

    def test_list_get(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
