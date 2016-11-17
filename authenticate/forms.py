from django import forms
from django.contrib.auth import authenticate
from nodes.models import Nodes
from users.models import User
from authentication import check_password, make_password


class AuthForm(forms.Form):
    label = forms.CharField(label=u'Label')
    secretkey = forms.CharField(label=u'Secret Key')

    def clean(self):
        try:
            self.node = Nodes.objects.get(
                label=self.cleaned_data.get('label'),
                secretkey=self.cleaned_data.get('secretkey')
            )
            return self.node
        except Nodes.DoesNotExist:
            raise forms.ValidationError("Node authenticate failure.")


class LoginForm(forms.Form):
    username = forms.CharField(label=u'Username')
    password = forms.CharField(label=u'Password',
                               widget=forms.PasswordInput(render_value=False))

    def clean(self):
        try:
            user = User.objects.get(username=self.cleaned_data.get('username'))

            if check_password(self.cleaned_data.get('password'), user.password):
                self.user = user
                return self.cleaned_data
        except User.DoesNotExist:
            raise forms.ValidationError("Unable to login with provided credentials.")