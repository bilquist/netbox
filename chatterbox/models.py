from django.db import models
from django.utils import timezone

# Create your models here.

class Post(models.Model):
	'''This class defines the chatters which users submit.'''
	# Define static values for Post moods
	POSITIVE = 'POS'
	NEGATIVE = 'NEG'
	NEUTRAL = 'NET'
	AMBIVALENT = 'AMB'
	NOMOOD = 'NOM'
	MOOD_CHOICES = (
		(POSITIVE, 'Positive'),
		(NEGATIVE, 'Negative'),
		(NEUTRAL, 'Neutral'),
		(AMBIVALENT, 'Ambivalent'),
		(NOMOOD, ''),
	)
	# Model fields
	author = models.ForeignKey('auth.User')
	text = models.TextField(max_length=255)
	mood = models.CharField(max_length=3, choices=MOOD_CHOICES, default=NOMOOD)
	published_date = models.DateTimeField(default=timezone.now)
	
	def __str__(self):
		'''Return the post field from our model.'''
		return self.post
