from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.post_list, name='post_list'),
	url(r'^graph$', views.graph, name='graph'),
	url(r'^sentiment_analysis$', views.sentiment_analysis, name='sentiment_analysis'),
	url(r'^d3js$', views.d3js, name='d3js'),
	url(r'^d3js2$', views.d3js2, name='d3js2'),
	url(r'^accounts/register/?$', views.register, name='register'),
	url(r'^accounts/profile/?$', views.update_profile, name='update_profile'),
	url(r'^lda_analysis$', views.lda_analysis, name='lda_analysis'),
]