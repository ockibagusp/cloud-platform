from django import forms
from supernodes.models import Supernodes
from users.models import User
from authentication import check_password


class SuperNodeAuthForm(forms.Form):
    user = forms.CharField(label=u'User')
    label = forms.CharField(label=u'Label')
    secretkey = forms.CharField(label=u'Secret Key')

    def clean(self):
        print self.cleaned_data.get('user')
        try:
            user = User.objects.get(username=self.cleaned_data.get('user'))
            self.supernode = Supernodes.objects.get(
                user=user.id,
                label=self.cleaned_data.get('label'),
                secretkey=self.cleaned_data.get('secretkey')
            )
            return self.supernode
        except (Supernodes.DoesNotExist, User.DoesNotExist):
            raise forms.ValidationError("Node authenticate failure.")


class UserAuthForm(forms.Form):
    username = forms.CharField(label=u'Username')
    password = forms.CharField(label=u'Password',
                               widget=forms.PasswordInput(render_value=False))

    def clean(self):
        try:
            user = User.objects.get(username=self.cleaned_data.get('username'))

            if check_password(self.cleaned_data.get('password'), user.password):
                self.user = user
                return self.cleaned_data
            raise forms.ValidationError("Unable to login with provided credentials.")
        except User.DoesNotExist:
            raise forms.ValidationError("Unable to login with provided credentials.")