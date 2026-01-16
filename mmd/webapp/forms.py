from user.models import MyUser as Utente
from django import forms

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'minlength': '8',
            'maxlength': '16',
            'pattern': r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,16}',
            'title': 'La password deve contenere almeno una lettera maiuscola, una minuscola, un numero e un carattere speciale.',
            'class': 'input'
        })
    )    
    class Meta:
        model = Utente
        fields = ['name','surname', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input','placeholder': 'Type here'}),
            'surname': forms.TextInput(attrs={'class': 'input ','placeholder': 'Type here'}),
            'email': forms.EmailInput(attrs={'class': 'input ', 'placeholder': 'Type here'}),
            'password': forms.PasswordInput(attrs={'class': 'input ','placeholder': 'Type here'}),
        }    
        
class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input validator',
            'placeholder': 'mail@site.com',
            'required': 'required'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input validator',
            'placeholder': 'Password',
            'required': 'required',
            'minlength': '8',
            'pattern': r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,16}',
            'maxlength': '16',
            'title': 'Must be more than 8 characters, including number, lowercase letter, uppercase letter'
        })
    )