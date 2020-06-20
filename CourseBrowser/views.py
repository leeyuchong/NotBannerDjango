from django.shortcuts import render
from .forms import SearchForm
from CourseBrowser.models import Courses, Profile
#from django.contrib.auth.form import UserCreationForm
#from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

def home(request):
    # Session variable to track where user is coming from
    request.session['currentPage']='home'

    # FORMS
    searchform = SearchForm()
    loginForm = AuthenticationForm()
    registrationForm = UserCreationForm(request.POST)

    args = {'searchform': searchform, 'loginForm': loginForm, 'registrationForm': registrationForm}

    # Retrieve the courses in the user's profile
    if request.user.is_authenticated:
        userRow = Profile.objects.get(user_id=request.user.id)
        selectedCourses = {}
        if userRow.cal1course1 != "blank": 
            selectedCourses["course1"]=Courses.objects.get(courseID=userRow.cal1course1)
        if userRow.cal1course2 != "blank": 
            selectedCourses["course2"]=Courses.objects.get(courseID=userRow.cal1course2)
        if userRow.cal1course3 != "blank": 
            selectedCourses["course3"]=Courses.objects.get(courseID=userRow.cal1course3)
        if userRow.cal1course4 != "blank": 
            selectedCourses["course4"]=Courses.objects.get(courseID=userRow.cal1course4)
        if userRow.cal1course5 != "blank": 
            selectedCourses["course5"]=Courses.objects.get(courseID=userRow.cal1course5)
        if userRow.cal1course6 != "blank": 
            selectedCourses["course6"]=Courses.objects.get(courseID=userRow.cal1course6)
        if userRow.cal1course7 != "blank":
            selectedCourses["course7"]=Courses.objects.get(courseID=userRow.cal1course7)
        args['selectedCourses'] = selectedCourses
    return render(request, 'CourseBrowser/home.html', args)

def search(request):
    # Session variable to track where user is coming from
    request.session['currentPage'] = 'search'
    
    # FORMS
    searchform = SearchForm()
    loginForm = AuthenticationForm()
    registrationForm = UserCreationForm(request.POST)
    
    args = {'loginForm': loginForm, 'registrationForm': registrationForm, 'searchform': searchform, }

    # Retrieve the courses in the user's profile
    if request.user.is_authenticated:
        userRow = Profile.objects.get(user_id=request.user.id)
        selectedCourses = {}
        if userRow.cal1course1 != "blank": 
            selectedCourses["course1"]=Courses.objects.get(courseID=userRow.cal1course1)
        if userRow.cal1course2 != "blank": 
            selectedCourses["course2"]=Courses.objects.get(courseID=userRow.cal1course2)
        if userRow.cal1course3 != "blank": 
            selectedCourses["course3"]=Courses.objects.get(courseID=userRow.cal1course3)
        if userRow.cal1course4 != "blank": 
            selectedCourses["course4"]=Courses.objects.get(courseID=userRow.cal1course4)
        if userRow.cal1course5 != "blank": 
            selectedCourses["course5"]=Courses.objects.get(courseID=userRow.cal1course5)
        if userRow.cal1course6 != "blank": 
            selectedCourses["course6"]=Courses.objects.get(courseID=userRow.cal1course6)
        if userRow.cal1course7 != "blank":
            selectedCourses["course7"]=Courses.objects.get(courseID=userRow.cal1course7)
        args['selectedCourses'] = selectedCourses

    # Check to see if user made a search. Add or delete course will get to the search page without a search query
    if request.method == 'GET':
        filled_form = SearchForm(request.GET)
        if filled_form.is_valid():
            inputString = filled_form.cleaned_data['searchTerm']
        else:
            inputString = request.session.get('passthroughSearch')
    else:
        inputString=request.get('passthroughsearch')

    # If user clicks on the link to the search page, there is no search query 
    if inputString == None:
        inputString = ''

    # Searching the database for the query. Create MySQL query manually to search all columns for the keyword
    searchResult = inputString
    args['searchedTerm'] = searchResult
    splitString = inputString.upper().split(' ')
    print(splitString)
    queryString = ""
    for s in splitString:
        if queryString != "":
            queryString+=" AND "
        if s == 'FR':
            queryString += "fr LIKE 1"
        elif s == 'NR' or s == 'NRO':
            queryString += 'gm LIKE "NR"'
        elif s == "SU":
            queryString += 'gm LIKE "SU"'
        elif s =='YL':
            queryString += "yl LIKE 1"
        elif s =='QA':
            queryString += "qa LIKE 1"
        elif s =='LA':
            queryString += "la LIKE 1"
        elif s == 'SP':
            queryString += "sp LIKE 1"
        elif s =='CLS':
            queryString += 'format LIKE "CLS"'
        elif s =='INT':
            queryString += 'format LIKE "INT"'
        elif s =='OTH':
            queryString += 'format LIKE "OTH"'
        elif s =='MON' or s == 'MONDAY':
            queryString += '((d1 LIKE "%%M%%") OR (d2 LIKE "%%M%%"))'
        elif s =='TUE'or s =='TUES'or s == 'TUESDAY':
            queryString += '(d1 LIKE "%%T%%") OR (d2 LIKE "%%T%%")'
        elif s =='WED' or s == 'WEDNESDAY':
            queryString += '(d1 LIKE "%%W%%") OR (d2 LIKE "%%W%%")'
        elif s =='THUR' or s == 'THURS' or s == 'THURSDAY':
            queryString += '(d1 LIKE "%%R%%") OR (d2 LIKE "%%R%%")'
        elif s =='FRI' or s == 'FRIDAY':
            queryString += '(d1 LIKE "%%F%%") OR (d2 LIKE "%%F%%")'
        elif s == '0.5' or s == '1.0' or s == '1.5':
            queryString += 'units LIKE '+ s
        else:
            if len(s) > 0 and s[0] == '0':
                # the starttimes are saved as int, so 0900 is saved is 900. Remove the leading 0 from search string.
                s = s[1:]
            queryString += "(courseID LIKE '%%"+s+"%%' OR title LIKE '%%"+s+"%%' OR loc LIKE '%%"+s+"%%' OR instructor LIKE '%%"+s+"%%' OR starttime1 LIKE '"+s+"%%' OR starttime2 LIKE '"+s+"%%' OR description LIKE '%%"+s+"%%')"
    
    sqlQuery = 'SELECT * FROM CourseBrowser_courses'
    if queryString != "":
        sqlQuery += " WHERE " + queryString

    print(sqlQuery)
    args['courses'] = Courses.objects.raw(sqlQuery)
    return render(request, 'CourseBrowser/search.html', args)

def signup(request):
    if request.method == 'POST':
        registrationForm = UserCreationForm(request.POST)
        if registrationForm.is_valid():
            registrationForm.save()
            username = registrationForm.cleaned_data.get('username')
            raw_password = registrationForm.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        registrationForm = UserCreationForm()
    return render(request, 'registration/signup.html', {'registrationForm': registrationForm})

def addCourse(request):
    # FORMS
    searchform = SearchForm()
    loginForm = AuthenticationForm()
    registrationForm = UserCreationForm(request.POST)

    # Skip check for request method because user can only access this view from an add button 
    request.session['passthroughSearch']  = request.POST.get('next', '')
        # request.POST.get('next', '') is used to extract the value of the name = 'next' field in the form in search.html. Used to redirect back to same search after add
    labelid=request.POST.get('courseid')
    print(labelid)
    current_user = request.user
    user_id=current_user.id
    user = User.objects.get(pk=user_id)
    if user.profile.cal1course1 == "blank": # blank is the default value
        user.profile.cal1course1 = labelid
    elif user.profile.cal1course2 == "blank":
        user.profile.cal1course2 = labelid
    elif user.profile.cal1course3 == "blank":
        user.profile.cal1course3 = labelid
    elif user.profile.cal1course4 == "blank":
        user.profile.cal1course4 = labelid
    elif user.profile.cal1course5 == "blank":
        user.profile.cal1course5=labelid
    elif user.profile.cal1course6 == "blank":
        user.profile.cal1course6 = labelid
    else:
        user.profile.cal1course7 = labelid
        # If all other course spots are taken, occupy the last spot
    user.save()

    args = {'searchform': searchform, 'loginForm': loginForm, 'registrationForm': registrationForm, }
    return HttpResponseRedirect('/search', args) # add button comes from a search result, redirect back to search

def deleteCourse(request):
    # FORMS
    searchform = SearchForm()
    loginForm = AuthenticationForm()
    registrationForm = UserCreationForm(request.POST)

    request.session['passthroughSearch']  = request.POST.get('next', '')
        # request.POST.get('next', '') is used to extract the value of the name = 'next' field in the form in search.html. Used to redirect back to same search after add
    labelid=request.POST.get('courseid')
    print(labelid)
    current_user = request.user
    user_id = current_user.id
    user = User.objects.get(pk=user_id)
    if user.profile.cal1course1 == labelid:
        user.profile.cal1course1="blank"
    elif user.profile.cal1course2 == labelid:
        user.profile.cal1course2="blank"
    elif user.profile.cal1course3 == labelid:
        user.profile.cal1course3="blank"
    elif user.profile.cal1course4 == labelid:
        user.profile.cal1course4="blank"
    elif user.profile.cal1course5 == labelid:
        user.profile.cal1course5="blank"
    elif user.profile.cal1course6 == labelid:
        user.profile.cal1course6="blank"
    else:
        user.profile.cal1course7="blank"
    user.save()

    args = {'searchform': searchform, 'loginForm': loginForm, 'registrationForm': registrationForm, }

    if request.session['passthroughSearch'] == '' and request.session['currentPage'] == "scheduler":
        # If user came from scheduler page without search
        return HttpResponseRedirect('/scheduler', args)
    elif request.session['currentPage'] == "home":
        # If user came from home page and has not done a search
        return HttpResponseRedirect('/', args)
    else: 
        return HttpResponseRedirect('/search', args)

def scheduler(request):
    # FORMS
    searchform = SearchForm()
    loginForm = AuthenticationForm()
    registrationForm = UserCreationForm(request.POST)

    args = {'searchform': searchform, 'loginForm': loginForm, 'registrationForm': registrationForm, }

    # Retrieve the courses in user's profile
    request.session['currentPage'] = "scheduler"
    if request.user.is_authenticated:
        selectedCourses = {}
        userRow = Profile.objects.get(user_id=request.user.id)
        if userRow.cal1course1 != "blank": 
            selectedCourses["course1"]=Courses.objects.get(courseID=userRow.cal1course1)
        if userRow.cal1course2 != "blank": 
            selectedCourses["course2"]=Courses.objects.get(courseID=userRow.cal1course2)
        if userRow.cal1course3 != "blank": 
            selectedCourses["course3"]=Courses.objects.get(courseID=userRow.cal1course3)
        if userRow.cal1course4 != "blank": 
            selectedCourses["course4"]=Courses.objects.get(courseID=userRow.cal1course4)
        if userRow.cal1course5 != "blank": 
            selectedCourses["course5"]=Courses.objects.get(courseID=userRow.cal1course5)
        if userRow.cal1course6 != "blank": 
            selectedCourses["course6"]=Courses.objects.get(courseID=userRow.cal1course6)
        if userRow.cal1course7 != "blank":
            selectedCourses["course7"]=Courses.objects.get(courseID=userRow.cal1course7)
        args['selectedCourses'] = selectedCourses
    return render(request, 'CourseBrowser/scheduler.html', args)

def datafest(request):
    return render(request, 'CourseBrowser/datafest.html')
