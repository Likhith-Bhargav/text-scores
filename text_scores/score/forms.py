from django import forms

class ScoreInputForm(forms.Form):
    text = forms.CharField(
        label='Enter your text',
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your text here...'}),
        max_length=500,
        required=True
    )
