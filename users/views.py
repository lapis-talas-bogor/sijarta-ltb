from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, reverse

from users.forms import PekerjaRegistrationForm, PenggunaRegistrationForm, UserLoginForm
from users.services.user_service import UserService
from users.utils.decorators import only_pengguna
from users.utils.jwt_utils import generate_jwt

# Create your views here.


def show_landing(request):

    context = {
        "user": request.user,
    }
    
    if not context["user"]["is_authenticated"]:
        return render(request, "show_landing.html")

    return redirect("service:show_homepage")


# @only_pengguna, as an example: only_pengguna is a decorator that checks if the user is authenticated and a pengguna.
def show_profile(request):
    pengguna_form = PenggunaRegistrationForm(request.user)
    pekerja_form = PekerjaRegistrationForm(request.user)

    if request.method == "POST":
        if request.user["is_pengguna"]:
            pengguna_form = PenggunaRegistrationForm(request.POST)
            if not pengguna_form.is_valid():
                return render(
                    request,
                    "show_profile.html",
                    {
                        "user": request.user,
                        "pengguna_form": pengguna_form,
                        "pekerja_form": pekerja_form,
                    },
                )

            name = request.POST["name"]
            password = request.POST["password"]
            gender = request.POST["gender"]
            phone_number = request.POST["phone_number"]
            birthdate = request.POST["birthdate"]
            address = request.POST["address"]

            if not UserService.check_password(password, request.user["password_hash"]):
                return JsonResponse({"message": "Invalid password"}, status=400)

            try:
                UserService.update_pengguna(
                    request.user["id"],
                    name,
                    password,
                    gender,
                    phone_number,
                    birthdate,
                    address,
                )
            except Exception as e:
                return JsonResponse(
                    {"message": "Failed to update user", "error": str(e)}, status=500
                )

            return redirect("user:show_profile")
        elif not request.user["is_pengguna"]:
            pekerja_form = PekerjaRegistrationForm(request.POST)
            if not pekerja_form.is_valid():
                return render(
                    request,
                    "show_profile.html",
                    {
                        "user": request.user,
                        "pengguna_form": pengguna_form,
                        "pekerja_form": pekerja_form,
                    },
                )

            name = request.POST["name"]
            password = request.POST["password"]
            gender = request.POST["gender"]
            phone_number = request.POST["phone_number"]
            birthdate = request.POST["birthdate"]
            address = request.POST["address"]
            bank_name = request.POST["bank_name"]
            bank_account_number = request.POST["bank_account_number"]
            npwp = request.POST["npwp"]
            photo_url = request.POST["photo_url"]

            if not UserService.check_password(password, request.user["password_hash"]):
                return JsonResponse({"message": "Invalid password"}, status=400)

            try:
                UserService.update_pekerja(
                    request.user["id"],
                    name,
                    password,
                    gender,
                    phone_number,
                    birthdate,
                    address,
                    bank_name,
                    bank_account_number,
                    npwp,
                    photo_url,
                )

            except Exception as e:
                return JsonResponse(
                    {"message": "Failed to update user", "error": str(e)}, status=500
                )

            return redirect("user:show_profile")

        else:
            return JsonResponse({"message": "Invalid user type"}, status=400)

    context = {
        "user": request.user,
        "pengguna_form": pengguna_form,
        "pekerja_form": pekerja_form,
    }

    return render(request, "show_profile.html", context)


def show_login(request):
    login_form = UserLoginForm()
    if request.method == "POST":
        login_form = UserLoginForm(request.POST)
        if not login_form.is_valid():
            return render(request, "show_login.html", {"form": login_form})

        phone_number = request.POST["phone_number"]
        password = request.POST["password"]

        user = UserService.get_user_by_phone_number(phone_number)
        if not user:
            return JsonResponse({"message": "User not found"}, status=404)

        if not UserService.check_password(password, user["password_hash"]):
            return JsonResponse({"message": "Invalid password"}, status=400)

        token = generate_jwt(str(user["id"]), user["name"])
        response = HttpResponseRedirect(reverse("service:show_homepage"))
        response.set_cookie("jwt", token, httponly=True, samesite="Strict", secure=True)

        return response

    return render(request, "show_login.html", {"form": login_form})


def register(request):
    pengguna_form = PenggunaRegistrationForm()
    pekerja_form = PekerjaRegistrationForm()
    if request.method == "POST":
        # Register user
        if request.POST["user_type"] == "pengguna":
            # Register pengguna
            pengguna_form = PenggunaRegistrationForm(request.POST)
            if not pengguna_form.is_valid():
                return render(
                    request,
                    "show_register.html",
                    {
                        "pengguna_form": pengguna_form,
                        "pekerja_form": pekerja_form,
                    },
                )

            name = request.POST["name"]
            password = request.POST["password"]
            gender = request.POST["gender"]
            phone_number = request.POST["phone_number"]
            birthdate = request.POST["birthdate"]
            address = request.POST["address"]

            try:
                UserService.create_pengguna(
                    name, password, gender, phone_number, birthdate, address
                )
            except Exception as e:
                return JsonResponse(
                    {"message": "Failed to register user", "error": str(e)}, status=500
                )

            return redirect("user:show_login")
        elif request.POST["user_type"] == "pekerja":
            # Register pekerja
            pekerja_form = PekerjaRegistrationForm(request.POST)
            if not pekerja_form.is_valid():
                return render(
                    request,
                    "show_register.html",
                    {
                        "pengguna_form": pengguna_form,
                        "pekerja_form": pekerja_form,
                        "show_pekerja": True,
                    },
                )

            name = request.POST["name"]
            password = request.POST["password"]
            gender = request.POST["gender"]
            phone_number = request.POST["phone_number"]
            birthdate = request.POST["birthdate"]
            address = request.POST["address"]
            bank_name = request.POST["bank_name"]
            bank_account_number = request.POST["bank_account_number"]
            npwp = request.POST["npwp"]
            photo_url = request.POST["photo_url"]

            try:
                UserService.create_pekerja(
                    name,
                    password,
                    gender,
                    phone_number,
                    birthdate,
                    address,
                    bank_name,
                    bank_account_number,
                    npwp,
                    photo_url,
                )
            except Exception as e:
                return JsonResponse(
                    {"message": "Failed to register user", "error": str(e)}, status=500
                )

            return redirect("user:show_login")
        else:
            return JsonResponse({"message": "Invalid user type"}, status=400)

    return render(
        request,
        "show_register.html",
        {"pengguna_form": pengguna_form, "pekerja_form": pekerja_form},
    )


def logout(request):
    response = HttpResponseRedirect(reverse("user:show_landing"))
    response.delete_cookie("jwt")
    return response
