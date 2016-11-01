from django import forms
from django.contrib.auth import authenticate
from nodes.models import Nodes


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
        user = authenticate(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password')
        )

        if user is not None:
            self.user = user
            return self.cleaned_data
        raise forms.ValidationError("Unable to login with provided credentials.")