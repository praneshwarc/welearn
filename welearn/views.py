from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers import serialize
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse

from .models import Course, Module, WeUser, Category, Option, Tier
from .forms import CourseForm, LoginForm, SignUpForm, ModuleForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizAttempt
from .forms import QuizForm


@login_required
def homepage(request):
    course_list = Course.objects.all()
    return render(request, 'homepage.html', {'courses': course_list})


@login_required
def course(request, course_id):
    selected_course = Course.objects.get(id=course_id)
    module_list = Module.objects.filter(course_id=course_id)
    return render(request, 'course_home.html', {'course': selected_course, 'modules': module_list})


def tutor_check(user):
    try:
        we_user = WeUser.objects.get(id=user.id)
    except WeUser.DoesNotExist:
        return False
    return we_user.is_tutor


@login_required
@user_passes_test(tutor_check, login_url='/home')
def tutor_courses(request):
    # POST for course creation/

    if request.method == 'GET':
        course_list = Course.objects.all()
        categories = Category.objects.all()

        return render(request, 'tutor_courses.html', {'courses': course_list, 'categories': categories})

    elif request.method == 'POST':
        course_form = CourseForm(request.POST)
        if course_form.is_valid():
            course = course_form.save(commit=False)
            tier = Tier.objects.get(label=course_form.cleaned_data['tier_name'])
            category = Category.objects.get(label=course_form.cleaned_data['category_name'])
            course.tier = tier
            course.category = category
            # print(myForm)
            we_user = WeUser.objects.get(id=request.user.id)
            course.tutor = we_user
            course.save()
            return HttpResponse(status=200)
        else:
            errors = course_form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)

@login_required
def tutor_courses_id(request, course_id):
    if request.method == 'GET':
        course_data = Course.objects.get(id=course_id);
        data = serialize("json", course_data, fields=('title', 'description'))
        return HttpResponse(data, content_type="application/json")

    if request.method == "POST":
        course = Course.objects.get(id=course_id)
        course_form = CourseForm(request.POST, instance=course)

        course_form.is_valid()
        course.title = course_form.cleaned_data.get("title", course.title)
        course.description = course_form.cleaned_data.get("description", course.description)
        course.hrs = course_form.cleaned_data.get("hrs", course.hrs)
        course.mins = course_form.cleaned_data.get("mins", course.mins)
        course.is_published = course_form.cleaned_data.get("is_published", course.is_published)
        if course_form.cleaned_data.get("tier_name", None):
            tier = Tier.objects.get(label=course_form.cleaned_data['tier_name'])
            course.tier = tier
        if course_form.cleaned_data.get("category_name", None):
            category = Category.objects.get(label=course_form.cleaned_data['category_name'])
            course.category = category
        course.save()
        return HttpResponse(status=200)

    if request.method == "DELETE":
        course_to_del = Course.objects.get(id=course_id)
        course_to_del.delete()
        return HttpResponse(status=204)


@login_required
# @user_passes_test(tutor_check)
def tutor_modules(request, course_id):
    if request.method == "GET":
        course = Course.objects.get(id=course_id);
        modules = course.modules.all()

        return render(request, "tutor_modules.html", {'course': course, 'modules': modules})
    elif request.method == "POST":
        module_form = ModuleForm(request.POST)
        if module_form.is_valid():
            module = module_form.save(commit=False)
            module.course = Course.objects.get(id=course_id)
            module.save()
            return
        else:
            errors = module_form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)


@login_required
def tutor_module_id(request, module_id):
    if request.METHOD == "GET":
        pass
    elif request.method == "POST":
        pass
    elif request.method =="DELETE":
        pass


# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if tutor_check(user):
                    return HttpResponseRedirect(reverse('welearn:tutor_courses'))
                else:
                    return HttpResponseRedirect(reverse('welearn:homepage'))
            else:
                loginForm = LoginForm()
                return render(request, 'loginpage.html',
                              {'loginForm': loginForm, 'error_message': 'Your account is disabled'})
        else:
            loginForm = LoginForm()
            return render(request, 'loginpage.html', {'loginForm': loginForm, 'error_message': 'Incorrect Credentials'})
    else:
        loginForm = LoginForm()
        return render(request, 'loginpage.html', {'loginForm': loginForm})


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse(('welearn:login')))


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = WeUser.objects.create_user(username=form.cleaned_data['username'],
                                              password=form.cleaned_data['password'],
                                              is_tutor=form.cleaned_data['is_tutor'],
                                              first_name=form.cleaned_data['first_name'],
                                              last_name=form.cleaned_data['last_name'])
            return redirect('welearn:login')
        else:
            return render(request, 'signup.html', {'signup_form': form, 'error_message': form.errors[0]})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'signup_form': form})


@login_required
def profile(request):
    print(request.user.first_name)
    return render(request, 'profile.html', {'user': request.user})


@login_required
def quiz_detail(request, module_id):
    quiz = get_object_or_404(Quiz, module__id=module_id)

    if request.method == 'POST':
        form = QuizForm(request.POST, quiz=quiz)
        if form.is_valid():
            score = 0
            for question in quiz.question_set.all():
                selected_option_id = form.cleaned_data[f'question_{question.id}']
                selected_option = get_object_or_404(Option, pk=selected_option_id)
                if selected_option.is_correct:
                    score += 1

            # Save the quiz attempt and score for the current user
            we_user = WeUser.objects.get(id=request.user.id)
            quiz_attempt, created = QuizAttempt.objects.get_or_create(user=we_user, quiz=quiz)
            quiz_attempt.score = score
            quiz_attempt.save()

            return redirect('welearn:quiz_result', module_id=module_id)
    else:
        form = QuizForm(quiz=quiz)

    context = {
        'quiz': quiz,
        'form': form,
    }

    return render(request, 'sample1.html', context)


@login_required
def quiz_result(request, module_id):
    quiz = get_object_or_404(Quiz, module__id=module_id)
    quiz_attempt = get_object_or_404(QuizAttempt, quiz__module__id=module_id, user__id=request.user.id)
    return render(request, 'sample2.html', {'quiz': quiz, 'score': quiz_attempt.score})
