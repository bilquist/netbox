from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.cache import cache
from django.db import connections, transaction
from django.db.models import Count, Case, IntegerField, Sum, When
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import Post, Profile, LDAViewParameters
from .forms import PostForm, SignUpForm, UserForm, ProfileForm, LDAOrganizationSelectionForm

# modeling imports
from chattertools import ChatterBox, SentimentTrain, LDACheckout

import json

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('post_list')
    else:
        form = SignUpForm()
    return render(request, 'chatterbox/register.html', {'form': form})

	
@login_required
@transaction.atomic
def update_profile(request):
	if request.method == 'POST':
		user_form = UserForm(request.POST, instance=request.user)
		profile_form = ProfileForm(request.POST, instance=request.user.profile)
		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, 'Your profile was successfully updated!')
			render(request, 'chatterbox/profile.html', {'user_form': user_form, 'profile_form': profile_form})
		else:
			messages.error(request, 'There were errors with your submission.')
	else:
		user_form = UserForm(instance=request.user)
		profile_form = ProfileForm(instance=request.user.profile)
	return render(request, 'chatterbox/profile.html', {'user_form': user_form, 'profile_form': profile_form})
	
	
# Create your views here.
@login_required
def post_list(request):
	# if this is a POST request we need to process the form data
	if request.method == "POST":
		# create a form instance and populate it with data from the request:
		form = PostForm(request.POST)
		# import our classifier
		classifier = get_cached_classifier()
		c = ChatterBox()
		# check whether form data is valid:
		if form.is_valid():
			post = form.save(commit=False)
			post.author = request.user
			post.published_date = timezone.now()
			print(post.text)
			post.sentiment = c.classify_text_sentiment(post.text, classifier=classifier)[1]
			post.save()
			return redirect('post_list')
	else:
		form = PostForm()
	posts = Post.objects.filter(author_id=request.user, published_date__lte=timezone.now()).order_by('-published_date')
	return render(request, 'chatterbox/post_list.html', {'posts': posts, 'form': form})
	
	
# Return an icon type for a given mood
def mood_icon(request, pk):
	# Grab the associated post
	post = get_object_or_404(Post, pk=pk)
	if post.mood == [choice[1] for choice in post.get_mood_choices() if choice[0] == 1][0]:
		return '<i class="material-icons">sentiment_very_satisified</i>' # positive
	elif post.mood == [choice[1] for choice in post.get_mood_choices() if choice[0] == 2][0]:
		return '<i class="material-icons">sentiment_very_dissatisified</i>' # negative
	elif post.mood == [choice[1] for choice in post.get_mood_choices() if choice[0] == 3][0]:
		return '<i class="material-icons">sentiment_neutral</i>' # neutral
	elif post.mood == [choice[1] for choice in post.get_mood_choices() if choice[0] == 4][0]:
		return '<i class="material-icons">sentiment_mood_bad</i>' # ambivalent
	else:
		return ''

	
def get_cached_classifier(affiliation=None):
    if affiliation == None:
	    key = "sentiment_classifier"
    else:
	    key = "sentiment_classifier_" + affiliation # provide a unique prefix
    history = cache.get(key) # try to read from cache
    if history is None:
        print("HERE SADLY")
        history = load_sentiment_model(affiliation)
        cache.set(key, history, 24*60*60)
    return history
	
	
def load_sentiment_model(affiliation=None):
	'''
	Load pre trained sentiment classifier.
	Ideally this should be unique for each organization.
	'''
	if affiliation == None:
		classifier_name = 'chatterbox_classifier'
	else:
		# TODO: look up unique classifier name by affiliation
		classifier_name = ''
	classifier = SentimentTrain.load_classifier(classifier_name)
	return classifier
	
	
	
@login_required
def sentiment_analysis(request):
	'''
	Display the sentiment information for our chatter
	For now only display on chatters which are classified
	'''
	# Chatter frequency line graph data
	data = Post.objects.filter(author_id=request.user) \
		.extra({'day':connections[Post.objects.db].ops.date_trunc_sql('day', 'published_date')}) \
		.values('day') \
		.annotate(c=Count('id')) \
		.order_by('day')
	json_list = []
	for item in data:
		json_list.append({'DateKey': item['day'].strftime('%Y-%m-%d'), 'ChatterCount': item['c']})
	chatter_freq_data = json.dumps(json_list)
	# Chatter sentiment distribution data
	data = Post.objects.filter(author_id=request.user) \
		.values('mood') \
		.annotate( \
			pos_count=Sum(Case(When(sentiment="pos", then=1), default=0), output_field=IntegerField()), \
			neg_count=Sum(Case(When(sentiment="neg", then=1), default=0), output_field=IntegerField()) \
		) \
		.order_by('mood')
	json_list = []
	for item in data:
		json_list.append({'Mood': item['mood'], 'PositiveCount': item['pos_count'], 'NegativeCount': item['neg_count']})
	chatter_sentiment_data = json.dumps(json_list)
	
	return render(request, 'chatterbox/sentiment_analysis.html', \
		{'chatter_freq_data': chatter_freq_data, 'chatter_sentiment_data': chatter_sentiment_data})

	
def graph(request):
    return render(request, 'chatterbox/graph.html')
	

def d3js(request):
    return render(request, 'chatterbox/d3js.html')

def d3js2(request):
    return render(request, 'chatterbox/d3js2.html')	
	
	
@login_required
def lda_analysis(request):
	'''
	Display the results of an LDA model analysis on the specified segment
	of user organization
	For now, allow all users to choose which organization they would like to seek
	In the future, limit admins to this functionality and allow individual users to
	only see the results from their individual organization
	'''
	# Call the LDA model for each organization
	# Later make this a drop down box so each organization is separate
	
	user_id = User.objects.filter(username=request.user).values('id')[0]['id']
	
	if request.method == "POST":
		# create a form instance and populate it with the data from the request
		print("POST REQUEST:")
		print(request.POST)
		form = LDAOrganizationSelectionForm(request.POST)
		# import our classifier
		# TODO!!!
		# check whether our form data is valid
		if form.is_valid():
			print('VALID FORM')
			post = form.save(commit=False)
			post.user_id = user_id
			post.save()
			return redirect('lda_analysis')
			
	else:
		try:
			data = LDAViewParameters.objects.get(user_id=user_id)
		except LDAViewParameters.DoesNotExist:
			print('Exception thrown!')
			data = None
		finally:
			if not data or data == "":
				query_data = Profile.objects.filter(user=request.user).values('organization')
				data = LDAViewParameters(user=request.user, organization=query_data[0]['organization'], \
					num_words=3, num_topics=5, num_passes=20, use_cached_model=False)
				#data = {'organization': query_data[0]['organization']}
		print('Data:')
		print(data)
		#instance_data = {'organization': 
		#form = LDAOrganizationSelectionForm(instance=request.user.profile)
		form = LDAOrganizationSelectionForm(instance=data)
		form.is_bound
	
	# If we are here, the form has been created with data elements
	# LDA model results takes: (lda_model, num_words, num_topics=None)
	param_organization = form['organization'].value()
	param_num_words = form['num_words'].value()
	param_num_topics = form['num_topics'].value()
	param_passes = form['num_passes'].value()
	param_load_cached_model = False # eventually update this
	
	
	
	# Elect to load a cached model instead of computing a new one
	if param_load_cached_model == True:
		#TODO: write API for loading models and getting the data from them
		print('TODO')
	else:
		# Get the proper chatter to classify
		#	1. Get all users in our selected organization
		related_users = Profile.objects.filter(organization=param_organization).values('user_id')
		#	2. Append all the chatter from such user into a list
		chatter = []
		for u in related_users:
			c_temp = Post.objects.filter(author_id=u['user_id']).values_list('text', flat=True)
			chatter = chatter + list(c_temp)
		print('Made it to the chatter call!')
		# LDACheckout is a front ender for the ChatterBox/LDA interface
		c, cm = LDACheckout.LDAModel(chatter, param_passes, param_num_topics, param_num_words, dictionary=None)
		lda_results = LDACheckout.LDAResults(c, cm, param_num_topics, param_num_words)
		
		# Print LDA Results (Eventually return these as a string through the render return)
		#print('LDA Results:')
		#print(lda_results)
	
	return render(request, 'chatterbox/lda_analysis.html', {'org_form': form, 'lda_result_string': lda_results})
	
	