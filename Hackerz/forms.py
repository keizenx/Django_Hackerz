from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Profile, Vendor


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=200, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
        return user


class LoginForm(forms.Form):
    username = forms.EmailField(label='Email')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Essayer de trouver l'utilisateur par email
            try:
                user = User.objects.get(email=username)
                # Utiliser le nom d'utilisateur pour l'authentification
                self.user_cache = authenticate(username=user.username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError(
                        "Veuillez saisir un email et un mot de passe valides. "
                        "Notez que les deux champs peuvent être sensibles à la casse."
                    )
            except User.DoesNotExist:
                # Essayer l'authentification directe (si username est aussi un nom d'utilisateur)
                self.user_cache = authenticate(username=username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError(
                        "Veuillez saisir un email et un mot de passe valides. "
                        "Notez que les deux champs peuvent être sensibles à la casse."
                    )
                    
        return self.cleaned_data
    
    def get_user(self):
        return getattr(self, 'user_cache', None)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'city', 'postal_code', 'country']
        widgets = {
            # Suppression de la référence à 'bio' ici
        }


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['shop_name', 'description', 'identity_document', 'logo', 'phone']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'identity_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(VendorForm, self).__init__(*args, **kwargs)
        self.fields['shop_name'].required = True
        self.fields['description'].required = True
        self.fields['identity_document'].required = True


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email'] 