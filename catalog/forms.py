from django import forms


class OptionForm(forms.Form):
    CHOICES = (
        ('name', 'nom'),
        ('nutri_score', 'nutriscore croissant'),
        ('-nutri_score', 'nutriscore décroissant'),
    )
    select = forms.ChoiceField(choices=CHOICES, label='Trié par',
                               widget=forms.Select(attrs={'onchange': 'form.submit();'}))