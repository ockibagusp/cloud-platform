from django import forms
from cloud_platform.helpers import is_objectid_valid


class NodePublishResetForm(forms.Form):
    id = forms.CharField()

    def clean(self):
        node_id = self.cleaned_data.get('id')
        if not is_objectid_valid(node_id):
            raise forms.ValidationError('%s is not valid ObjectId.' % node_id)
        return self.cleaned_data
