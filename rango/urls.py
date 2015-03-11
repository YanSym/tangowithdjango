from django.conf.urls import patterns, url
from rango import views


urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),
	url(r'^add_category/$', views.add_category, name='add_category'), # NEW MAPPING!
	url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'), # NEW MAPPING!
	url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
	url(r'^restricted/', views.restricted, name='restricted'),
	
	#new profile related urls
	url(r'^profile/$', views.profile, name='profile'),
	
	url(r'^add_profile/$', views.registerprofile, name='add_profile'),
	
	url(r'^profile/(?P<user_id>[0-9]+)/$', views.profile, name='profile'),
	
	url(r'^edit_profile/$', views.editprofile, name='edit_profile'),
	
	url(r'^users/$', views.userlist, name='user_list'),

	#url to track urls of pages to get views
        url(r'^goto/$', views.track_url,  name='goto'),
	
	#removed urls
	#url(r'^search/', views.search, name='search'),
	# url(r'^register/$', views.register, name='register'),
	# url(r'^search/', views.search, name='search'),

	#url(r'^login/$', views.user_login, name='login'),
	#url(r'^logout/$', views.user_logout, name='logout'),
	#url(r'^register/$', views.register, name='register'),
)
