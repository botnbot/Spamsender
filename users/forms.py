from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    avatar = forms.ImageField(required=False, label="Аватар")
    phone = forms.CharField(required=False, label="Телефон")
    country = forms.CharField(required=False, label="Страна")

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "avatar", "phone", "country")
