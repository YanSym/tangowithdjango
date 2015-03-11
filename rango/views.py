from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.forms import CategoryForm
from rango.forms import PageForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from rango.bing_search import run_query

#new
from django.contrib.auth.models import User


# Import the Category model
from rango.models import Category
from rango.models import Page
from rango.models import UserProfile

from rango.forms import UserForm, UserProfileForm


def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})



def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits


    response = render(request,'rango/index.html', context_dict)

    return response
	

	
def about(request):

    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'aboutboldmessage': "This tutorial has been put together by Yan Vianna Sym, ID: 2165508", 'visits': count}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.

    return render(request, 'rango/about.html', context_dict)
	
	
def category(request, category_name_slug):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}
	
    context_dict['result_list'] = None
    context_dict['query'] = None
    if request.method == 'POST':
		try:
			query = request.POST['query'].strip()

			if query:
				result_list = run_query(query)
    
				context_dict['result_list'] = result_list
				context_dict['query'] = query
				
		except:
			pass

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.

        category = Category.objects.get(slug=category_name_slug)

        temp = Category.objects.filter(slug=category_name_slug)
        category = temp[0]

		
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
		
        context_dict['category_name_slug'] = category_name_slug
		
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

		
    if not context_dict['query']:
        context_dict['query'] = category.name

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)
	
	
@login_required
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})
	
	
@login_required

def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
                cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category': cat, 'category_name_slug':category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)

	
def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
        try:
            page = Page.objects.get( id = page_id )
            page.views =  (page.views + 1)
	        #saves result
            page.save()
            url = page.url
    
        except:
            pass
	
    return redirect(url)

			
def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
			# Bad login details were provided. So we can't log the user in.
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html', {})
		
@login_required
def profile(request, user_id = None):
    if user_id is not None:
        context_dict = {'user': User.objects.get(id=user_id)}
    else:
        context_dict = {'user': User.objects.get(id=request.user.id)}
    try:
        context_dict['profile'] = UserProfile.objects.get(user=context_dict['user'])
    except:
        context_dict['profile'] = None
    context_dict['myprofile'] = user_id is None or user_id == request.user.id
    return render(request, 'registration/profile.html', context_dict)
	
@login_required
def registerprofile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = User.objects.get(id=request.user.id)
            if 'picture' in request.FILES:
                try:
                    profile.picture = request.FILES['picture']
                except:
                    pass
            profile.save()
            return redirect('index')
    else:
        profile_form = UserProfileForm()
    return render(request, 'registration/profileregistration.html', {'profile_form': profile_form})
	
@login_required
def editprofile(request):
    try:
        users_profile = UserProfile.objects.get(user=request.user)
    except:
        users_profile = None
    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST, instance=users_profile)
        if profile_form.is_valid():
            profile_updated = profile_form.save(commit=False)
            if users_profile is None:
                profile_updated.user = User.objects.get(id=request.user.id)
            if 'picture' in request.FILES:
                try:
                    profile_updated.picture = request.FILES['picture']
                except:
                    pass
            profile_updated.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=users_profile)
        return render(request, 'registration/profileedit.html', {'profile_form': form})
		
@login_required
def userlist(request):

    users = User.objects.all()
	
    return render(request, 'registration/userlist.html', {'users': users})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit = True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})
	
@login_required
def restricted(request):
	context_dict = {}
	context_dict['message'] = "Since you're logged in, you can see this text!"
	
	return render(request,"rango/restricted.html", context_dict)	
	

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')
