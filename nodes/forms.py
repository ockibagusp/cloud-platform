from django import forms
from cloud_platform.helpers import is_objectid_valid


class NodePublishResetForm(forms.Form):
    id = forms.CharField()

    def clean(self):
        node_id = self.cleaned_data.get('id')
        if not is_objectid_valid(node_id):
            raise forms.ValidationError('%s is not valid ObjectId.' % node_id)
        return self.cleaned_data


class NodeDuplicateForm(forms.Form):
    id = forms.CharField(required=True)
    count = forms.IntegerField(required=True)

    def clean(self):
        node_id = self.cleaned_data.get('id')
        copy_count = self.cleaned_data.get('count')
        if not is_objectid_valid(node_id):
            raise forms.ValidationError('%s is not valid ObjectId.' % node_id)
        if 1 > copy_count < 100:
            raise forms.ValidationError('duplicate copy count must be in range of 1 to 100.')
        return self.cleaned_data
