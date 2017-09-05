from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post, Profile, LDAViewParameters

# If we want to add fields to the registration form, see:
# https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
#first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
class PostForm(forms.ModelForm):

	class Meta:
		model = Post
		fields = ('text', 'mood',)
		
		
class SignUpForm(UserCreationForm):
	first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
	last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
	
	class Meta:
		model = User
		fields = ('username', 'password1', 'password2', 'first_name', 'last_name')

		
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email')
		
class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('organization', 'location', 'birth_date', 'bio')
		
class LDAOrganizationSelectionForm(forms.ModelForm):
	class Meta:
		model = LDAViewParameters
		fields = ('organization', 'num_words', 'num_topics', 'num_passes', 'use_cached_model')

	