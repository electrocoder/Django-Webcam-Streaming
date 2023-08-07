from django import forms



class EmailForm(forms.Form):
    email = forms.EmailField(label='E-posta adresi')
    name  = forms.CharField(max_length=100)
    image = forms.CharField(widget=forms.Textarea(attrs={"rows":"5"}))
    phone = forms.CharField(max_length=15)
