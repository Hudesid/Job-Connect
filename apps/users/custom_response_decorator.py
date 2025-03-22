from rest_framework.views import APIView
from rest_framework import status


"""
response structure

{
    status: True or False,
    message: "something"
    errors: {},
    data: {}
}
"""

codes = {
    "400": "Noto'g'ri ma'lumot kiritilgan.",
    "404": "DataNotFound",
    "register": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tkazildi",
    "login": "Tizimga muvaffaqiyatli kirildi.",
    "refresh": "Token muvaffaqiyatli yangilandi.",
    "verify_email": "Email tekshirishdan muvaffaqiyatli o'tdi.",
    "recovery_password": "Password muvaffaqiyatli yangilandi.",
    "logout": "Foydalanuvchi tizimdan muvaffaqiyatli chiqdi.",
    "job_seeker_create": "Ish qidiruvchi profili muvaffaqiyatli yaratildi.",
    "my_profile": "Foydalanuvchi malumotlari muvaffaqiyatli olindi.",
    "my_profile_update": "Foydalanuvchi ma'lumotlari muvaffaqiyatli yangilandi.",
    "resume_upload": "Rezyume muvaffaqiyatli yuklandi.",
    "company_create": "Kompaniya profili muvaffaqiyatli yaratildi.",
    "companies_list": "Kompaniyalar ro'yxati muvaffiqiyatli olindi.",
    "company_detail": "Companiya ma'lumoti muvaffaqiyatli olindi.",
    "my_company": "Sizga tegishli kompaniya ma'lumotlari muvaffaqiyatli olindi.",
    "users_stats": "Foydalanuvchilar statistikasi muvaffaqiyatli olindi.",
    "skills": "Ko'nikma muvaffaqiyatli qo'shildi.",
    "skills_detail": "Ko'nikmalar ro'yxati muvaffaqiyatli olindi.",
    "notifications_list": "Bildirishnomalar ro'yxati muvaffaqiyatli olindi.",
    "notification_status_read": "Bildirishnoma o'qilgan deb belgilandi.",
    "notifications_status_read": "Barcha bildirishnomalar o'qilgan deb belgilandi.",
    "post_create": "Vakansiya muvaffaqiyatli e'lon qilindi.",
    "posts_list": "Vakansiyalar ro'yxati muvaffaqiyatli olindi.",
    "post_detail": "Vakansiya ma'lumotlari muvaffaqiyatli olindi.",
    "post_update": "Vakansiya ma'lumotlari muvaffaqiyatli yangilandi.",
    "post_delete": "Vakansiya muvaffaqiyatli o'chirildi.",
    "posts_recommended": "Tavsiya etilgan vakansiyalar muvaffaqiyatli olindi.",
    "job_application_create": "Ariza muvaffaqiyatli topshirildi.",
    "job_application_list": "Arizalar ro'yxati muvaffaqiyatli olindi.",
    "job_application_detail": "Ariza ma'lumotlari muvaffaqiyatli olindi.",
    "my_application_update": "Ariza muvaffaqiyatli yangilandi.",
    "my_application_delete": "Ariza muvaffaqiyatli o'chirildi.",
    "post_applications": "Vakansiyaga kelib tushgan arizalar ro'yxati muvaffaqiyali olindi.",
    "saved_job_list": "Saqlangan vakansiyalar ro'yxati olindi.",
    "saved_job": "Vakansiya muvaffaqiyatli saqlandi.",
    "saved_job_delete": "Saqlangan vakansiya muvaffaqiyatli o'chirildi.",
    "job_posting_stats": "Vakansiyalar statistikasi muvaffaqiyatli olindi.",
    "job_application_stats": "Arizalar statistikasi muvaffaqiyatli olindi.",
    "search": "Ma'lumotlar muvaffaqiyatli olindi."
}


def custom_response(mark):
    def decorator(view):
        def inner(self, request, *args, **kwargs):
            response = super(view, self).dispatch(request, *args, **kwargs)
            response_data = response.data
            data = dict(
                status=True,
                message="",
                errors={},
                data={},
            )
            if response.exception:
                data["status"] = False
                if response.status_code == status.HTTP_400_BAD_REQUEST:
                    data["message"] = codes["400"]
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    data['message'] = codes['404']
                data['errors'] = response_data
            else:
                data["data"] = (response_data.get("user") if mark in ["verify_email", "recovery_password", "logout"] else response_data)
                if mark == "login":
                    data['message'] = codes['login']
                elif mark == "register":
                    data['message'] = codes['register']
                elif mark == "refresh":
                    data['message'] = codes['refresh']
                elif mark == "verify_email":
                    data['message'] = codes['verify_email']
                elif mark == "forgot_password":
                    data['message'] = f"'{response_data.get("email")}' ga habar jo'natildi."
                elif mark == "recovery_password":
                    data['message'] = (codes['verify_email'] if request.method == 'GET' else codes['recovery_password'])
                elif mark == "logout":
                    data['message'] = codes['logout']
                elif mark == "job_seeker_create":
                    data['message'] = codes['job_seeker_create']
                elif mark == "my_profile":
                    data['message'] = (codes['my_profile_update'] if request.method in ('PUT', 'PATCH') else codes['my_profile'])
                elif mark == "user_profile":
                    data['message'] = codes['my_profile']
                elif mark == "resume_upload":
                    data['message'] = codes['resume_upload']
                elif mark == "company_create":
                    data['message'] = codes['company_create']
                elif mark == "companies_list":
                    data['message'] = codes['companies_list']
                elif mark == "company_detail":
                    data['message'] = codes['company_detail']
                elif mark == "my_company":
                    data['message'] = codes['my_company']
                elif mark == "users_stats":
                    data['message'] = codes['users_stats']
                elif mark == "skills":
                    data['message'] = (codes['skills_detail'] if request.method == 'GET' else codes['skills'])
                elif mark == "notifications_list":
                    data['message'] = codes['notifications_list']
                elif mark == "notification_status_read":
                    data['message'] = codes['notification_status_read']
                elif mark == "notifications_status_read":
                    data['message'] = codes['notifications_status_read']
                elif mark == "posts_list":
                    data['message'] = codes['posts_list']
                elif mark == "post_detail":
                    data['message'] = (codes['post_detail'] if request.method == 'GET' else codes['post_delete'] if request.method == 'DELETE' else codes['post_update'])
                elif mark == "posts_recommended":
                    data['message'] = codes["posts_recommended"]
                elif mark == "job_application_list_and_post":
                    data['message'] =(codes['job_application_list'] if request.method == 'GET' else codes["job_application_create"])
                elif mark == "job_application_detail":
                    data['message'] = codes["job_application_detail"]
                elif mark == "my_application":
                    data['message'] = (codes['my_application_delete'] if request.method == 'DELETE' else codes["job_application_detail"] if request.method == 'GET' else codes['my_application_update'])
                elif mark == "post_applications":
                    data['message'] = codes["post_applications"]
                elif mark == "saved_job_list":
                    data['message'] = codes["saved_job_list"]
                elif mark == "saved_job":
                    data['message'] = codes["saved_job"]
                elif mark == "saved_job_delete":
                    data['message'] = codes["saved_job_delete"]
                elif mark == "job_posting_stats":
                    data['message'] = codes["job_posting_stats"]
                elif mark == "job_application_stats":
                    data['message'] = codes["job_application_stats"]
                elif mark == "search":
                    data['message'] = codes["search"]
            response.data = data
            return response

        assert issubclass(view, APIView), (
            "class %s must be subclass of APIView" % view.__class__
        )

        view.dispatch = inner
        return view
    return decorator