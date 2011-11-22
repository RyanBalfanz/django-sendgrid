from django import forms

class EmailForm(forms.Form):
	subject = forms.CharField(max_length=100)
	message = forms.CharField()
	sender = forms.EmailField()
	to = forms.EmailField()
