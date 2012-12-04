from django import forms


class EmailForm(forms.Form):
	subject = forms.CharField(max_length=100)
	message = forms.CharField(widget=forms.Textarea)
	sender = forms.EmailField()
	to = forms.EmailField()
	categories = forms.CharField(help_text="CSV", required=False, widget=forms.Textarea)
	html = forms.BooleanField(initial=False, required=False)
	enable_gravatar = forms.BooleanField(initial=False, required=False)
	enable_click_tracking = forms.BooleanField(initial=False, required=False)
	add_unsubscribe_link = forms.BooleanField(initial=False, required=False)
