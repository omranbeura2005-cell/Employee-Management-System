from django import forms
from django.contrib.auth.models import User
from .models import Employee

class EmployeeForm(forms.ModelForm):
    username = forms.CharField(required=False, help_text='Login username for this employee.')
    password = forms.CharField(required=False, widget=forms.PasswordInput, help_text='Set or replace the login password.')

    class Meta:
        model = Employee
        exclude = ('user',)
        widgets = {
            'joining_date' :forms.DateInput(attrs = {'type' : 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if username:
            users = User.objects.filter(username__iexact=username)
            if self.instance.user_id:
                users = users.exclude(pk=self.instance.user_id)
            if users.exists():
                raise forms.ValidationError('That username is already in use.')
        return username

    def save(self, commit=True):
        employee = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username:
            user = employee.user or User()
            user.username = username
            user.email = employee.email
            if password:
                user.set_password(password)
            elif not user.pk:
                user.set_unusable_password()
            user.save()
            employee.user = user
        if commit:
            employee.save()
        return employee