from django import forms

class EmailForm(forms.Form):
	subject = forms.CharField(max_length=100)
	message = forms.CharField()
	sender = forms.EmailField()
	to = forms.EmailField()
	category = forms.CharField(max_length=100, required=False)
	html = forms.BooleanField(initial=False, required=False)
	enable_gravatar = forms.BooleanField(initial=False, required=False)
	enable_click_tracking = forms.BooleanField(initial=False, required=False)
	add_unsubscribe_link = forms.BooleanField(initial=False, required=False)
