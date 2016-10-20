from django import forms
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
