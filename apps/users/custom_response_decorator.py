from rest_framework.views import APIView
from rest_framework import status


"""
response structure

{
    status_code : 200,
    errors {},
    data {}
}
"""

codes = {
    "400": "Noto'g'ri ma'lumot kiritilgan.",
    "register": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tkazildi",
    "login": "Tizimga muvaffaqiyatli kirildi.",
    "refresh": "Token muvaffaqiyatli yangilandi.",
    "verify_email": "Email tekshirishdan muvaffaqiyatli o'tdi.",
    "recovery_password": "Password muvaffaqiyatli yangilandi.",
    "logout": "Foydalanuvchi tizimdan muvaffaqiyatli chiqdi."
}


def custom_response(mark):
    def decorator(view):
        def inner(self, request, *args, **kwargs):
            response = super(view, self).dispatch(request, *args, **kwargs)
            list_errors = []
            response_data = response.data
            data = dict(
                status=True,
                message="",
                errors=list_errors,
                data={},
            )
            if response.exception:
                data["status"] = False
                errors = response_data.get("errors", [])
                for e in errors:
                    field = e.get("field")
                    message = e.get("message")
                    if isinstance(message, list):
                        message_ = message[0]
                    else:
                        message_ = message
                    error_data = {
                        "field": field,
                        "message": message_,
                    }
                    if hasattr(message_, 'code'):
                        error_data["code"] = message_.code.upper()
                    list_errors.append(error_data)
                data["errors"] = list_errors
                if response.status_code == status.HTTP_400_BAD_REQUEST:
                    if "error" in response_data:
                        data["message"] = response_data["error"]
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
            response.data = data
            return response

        assert issubclass(view, APIView), (
            "class %s must be subclass of APIView" % view.__class__
        )

        view.dispatch = inner
        return view
    return decorator