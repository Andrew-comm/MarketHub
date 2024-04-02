from django.contrib.auth.models import User
from django import forms



class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    email = forms.EmailField(label='Email')
    phone_number = forms.CharField(label='Phone Number')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']

    def clean_confirm_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.email = self.cleaned_data["email"]
        user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            user.save()
        return user