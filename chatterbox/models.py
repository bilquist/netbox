from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Profile(models.Model):
	user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	organization = models.CharField(max_length=30, blank=True)
	bio = models.TextField(max_length=500, blank=True)
	location = models.CharField(max_length=30, blank=True)
	birth_date = models.DateField(null=True, blank=True)
	
	def __str__(self):  # __unicode__ for python 2
		return self.user.username
	
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	instance.profile.save()
		
	
	
class Post(models.Model):
	'''This class defines the chatters which users submit.'''
	# Define static values for Post moods
	NOMOOD = 'No Mood'
	POSITIVE = 'Positive'
	NEGATIVE = 'Negative'
	NEUTRAL = 'Neutral'
	AMBIVALENT = 'Ambivalent'
	MOOD_CHOICES = (
		(NOMOOD, ''),
		(POSITIVE, 'Positive'),
		(NEGATIVE, 'Negative'),
		(NEUTRAL, 'Neutral'),
		(AMBIVALENT, 'Ambivalent'),
	)
	# Model fields
	author = models.ForeignKey('auth.User')
	text = models.TextField(max_length=255)
	mood = models.CharField(max_length=15, choices=MOOD_CHOICES, default=NOMOOD)
	published_date = models.DateTimeField(default=timezone.now)
	sentiment = models.TextField(max_length=255, default='')
	
	def __str__(self):
		'''Return the post field from our model.'''
		return self.text

	def get_mood_choices(self):
		'''Return the tuple of MOOD_CHOICES'''
		return MOOD_CHOICES
		

	
class LDAViewParameters(models.Model):
	'''This class holds the values chosen for the LDA view's parameters'''
	
	# Get list of distinct organizations
	profile_orgs = Profile.objects.values_list('organization').distinct()
	profile_choices = list(zip(tuple(x[0] for x in profile_orgs), tuple(y[0] for y in profile_orgs)))
	#print(list(profile_choices))
	
	# Model fields
	#user = models.ForeignKey('auth.User')
	user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
	organization = models.CharField(max_length=30, choices=profile_choices)
	num_words = models.PositiveSmallIntegerField(default=3, blank=False, null=False)
	num_topics = models.PositiveSmallIntegerField(default=5, blank=False, null=False)
	num_passes = models.PositiveSmallIntegerField(default=20, blank=False, null=False)
	use_cached_model = models.BooleanField(default=False, blank=False, null=False)
	