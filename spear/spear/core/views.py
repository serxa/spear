from django.http import HttpResponseRedirect
from django import forms
from django.shortcuts import render
from django.contrib import auth

# Form to authenticate against django userbase
class LoginForm(forms.Form):
    userid = forms.CharField(label = 'User ID')
    password = forms.CharField(label = 'Password', widget=forms.PasswordInput)
    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        userid = cleaned_data.get('userid')
        password = cleaned_data.get('password')
        user = auth.authenticate(username=userid, password=password)
        if user is not None:
            if user.is_active:
                cleaned_data['user'] = user
                return cleaned_data
            else:
                self._errors['userid'] = self.error_class(['User blocked'])
        else:
            self._errors['password'] = self.error_class([u'Wrong ID or password'])
        del cleaned_data['password']

def login(request):
    if request.method == 'POST':
        # get userid, password
        loginform = LoginForm(request.POST)
        if loginform.is_valid():
            auth.login(request, loginform.cleaned_data['user'])
            return HttpResponseRedirect('/')
    else:
        loginform = LoginForm()
    return render(request, 'core/login.html', {'authform':loginform})

