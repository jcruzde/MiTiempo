from django import forms

class Form_login(forms.Form):
    usuario = forms.CharField(label='usuario', widget=forms.TextInput)
    contraseña = forms.CharField(label='contraseña', widget=forms.PasswordInput)
