import re
from django import forms

class TopUpForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    nominal = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={"placeholder": "Nominal"})
    )

