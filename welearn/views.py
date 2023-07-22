import os

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers import serialize
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator

from .models import Course, Module, WeUser, Category, Option, Tier, Content, Question
from .forms import CourseForm, LoginForm, SignUpForm, ModuleForm, ModuleEditForm, QuizForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizAttempt
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt



def tutor_check(user):
    try:
        we_user = WeUser.objects.get(id=user.id)
    except WeUser.DoesNotExist:
        return False
    return we_user.is_tutor


@login_required
def student_home(request):
    course_list = Course.objects.all()
    return render(request, 'student_home.html', {'courses': course_list})


@login_required
def course(request, course_id):
    selected_course = Course.objects.get(id=course_id)
    module_list = Module.objects.filter(course_id=course_id)
    return render(request, 'course.html', {'course': selected_course, 'modules': module_list})


@login_required
def profile(request):
    try:
        we_user = WeUser.objects.get(id=request.user.id)
        student_count = Course.objects.filter(tutor=we_user).aggregate(student_count=Count('registered_users'))['student_count']
    except WeUser.DoesNotExist:
        return False

    print(we_user)

    return render(request, 'profile.html', {'user': we_user, 'student_count': student_count})

@login_required
@user_passes_test(tutor_check, login_url='/home')
def tutor_home(request):
    # POST for course creation/

    if request.method == 'GET':
        course_list = Course.objects.filter(tutor_id=request.user.id)
        categories = Category.objects.all()

        return render(request, 'tutor_courses.html', {'courses': course_list, 'categories': categories})


def courses(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        if course_form.is_valid():
            course = course_form.save(commit=False)
            tier = Tier.objects.get(label=course_form.cleaned_data['tier_name'])
            category = course_form.cleaned_data['category']
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
def tutor_course_id(request, course_id):
    if request.method == 'GET':
        course_data = Course.objects.get(id=course_id)
        data = serialize("json", [course_data])
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
        modules = course.modules.all();
        #print(modules[0].quiz)
        return render(request, "tutor_modules.html", {'course': course, 'modules': modules})
    elif request.method == "POST":
        module_form = ModuleForm(request.POST)
        if module_form.is_valid():
            module = module_form.save(commit=False)
            module.course = Course.objects.get(id=course_id)
            module.save()
            return HttpResponse(status=200)
        else:
            errors = module_form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)


#@login_required
# @csrf_exempt # use this while testing from postman
def tutor_module_id(request, module_id):
    if request.method == "GET":
        module = get_object_or_404(Module, id=module_id)
        contents = Content.objects.filter(module=module)

        content_data = []
        for content in contents:
            filename = os.path.basename(content.file.name)
            content_info = {
                'id': content.id,
                'file': filename,
            }
            content_data.append(content_info)

        module_data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'contents': content_data,
        }

        return JsonResponse(module_data)
    elif request.method == "POST":
        module = get_object_or_404(Module, id=module_id)
        module_form = ModuleEditForm(request.POST, instance=module)

        if module_form.is_valid():
            edit_module = module_form.save(commit=False)
            edit_module.title = module_form.cleaned_data.get("title", module.title)
            edit_module.description = module_form.cleaned_data.get("description", module.description)
            module_data = {
                'id': edit_module.id,
                'title': edit_module.title,
                'description': edit_module.description,
            }
            edit_module.save()
            return JsonResponse(module_data)
        else:
            errors = module_form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)
    elif request.method == "DELETE":
        module_to_del = Module.objects.get(id=module_id)
        module_to_del.delete()
        return HttpResponse(status=204)





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
                    return HttpResponseRedirect(reverse('welearn:tutor_home'))
                else:
                    return HttpResponseRedirect(reverse('welearn:student_home'))
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
            quiz_attempt.max_score = quiz.question_set.count()
            quiz_attempt.save()

            return redirect('welearn:quiz_result', module_id=module_id)
    else:
        form = QuizForm(quiz=quiz)

    context = {
        'quiz': quiz,
        'form': form,
    }

    return render(request, 'quiz_page.html', context)



@login_required
def quiz_result(request, module_id):
    quiz = get_object_or_404(Quiz, module__id=module_id)
    quiz_attempt = get_object_or_404(QuizAttempt, quiz__module__id=module_id, user__id=request.user.id)
    return render(request, 'quiz_result.html', {'quiz': quiz, 'score': quiz_attempt.score})



class AddContent(View):

    def get(self, request, module_id):
        module = Module.objects.get(pk=module_id)
        return render(request, 'sample3.html', {'module': module})

    def post(self, request, module_id):
        module = Module.objects.get(pk=module_id)
        print(request.POST)
        if request.FILES:
            file = request.FILES['file']
            Content.objects.create(module=module, file=file)
            return HttpResponse(status=201)
        else:
            print(request.POST['youtube_link'])
            link = request.POST['youtube_link']
            Content.objects.create(module=module, youtube_video=link)
            return HttpResponse(status=201)




class ContentView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, content_id):
        content = get_object_or_404(Content, pk=content_id)
        content.delete()
        return HttpResponse(status=204)


@csrf_exempt
def create_quiz(request, module_id):
    if request.method == 'POST':
        print("CREATING QUIZ")
        module = get_object_or_404(Module, pk=module_id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

        if 'title' not in data or 'description' not in data or 'questions' not in data:
            return JsonResponse({'error': 'Invalid data format.'}, status=400)

        if Quiz.objects.filter(module=module).exists():
            return JsonResponse({'error': 'This module already has a quiz.'}, status=400)

        quiz_data = {
            'module': module,
            'title': data['title'],
            'description': data['description'],
            'grade_required': data.get('grade_required', 0),  # Add default value if not provided
        }

        quiz = Quiz()
        quiz.module = module
        quiz.title = data["title"]
        quiz.description = data['description'],
        quiz.grade_required = data.get('grade_required', 0)
        quiz.save()
        count = 0
        for question_data in data['questions']:
            if count == 0:
                count = 1
                continue

            if 'text' not in question_data or 'options' not in question_data:
                return JsonResponse({'error': 'Invalid question format.'}, status=400)

            question = Question.objects.create(quiz=quiz, text=question_data['text'])
            count = 0

            for option_data in question_data['options']:
                if count == 0:
                    count = count + 1
                    continue
                coption = int(question_data.get("correct_option", 1))
                if count == coption:
                    option_data["is_correct"] = True
                else:
                    option_data['is_correct'] = False
                count = count + 1
                if 'text' not in option_data or 'is_correct' not in option_data:
                    return JsonResponse({'error': 'Invalid option format.'}, status=400)

                Option.objects.create(question=question, text=option_data['text'], is_correct=option_data['is_correct'])

        return JsonResponse({'message': 'Quiz created successfully.'}, status=201)

    return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)


def create_quiz_page(request, module_id):

    return render(request, 'dummy2.html', {'module_id': module_id})


class DeleteQuiz(View):
    def delete(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        quiz.delete()
        return HttpResponse(status=204)

