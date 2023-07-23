import os
import re
from datetime import date, datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers import serialize
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.db.models import Q

from .models import Course, Module, WeUser, Category, Option, Tier, Content, Question, UserBillingInfo, Mail
from .forms import CourseForm, LoginForm, SignUpForm, ModuleForm, ModuleEditForm, QuizForm, PaymentForm, \
    BillingInfoForm, MailForm, ReplyForm
from django.contrib.auth.decorators import login_required
from .models import Quiz, QuizAttempt
from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO


def tutor_check(user):
    try:
        we_user = WeUser.objects.get(id=user.id)
    except WeUser.DoesNotExist:
        return False
    return we_user.is_tutor

def student_check(user):
    try:
        we_user = WeUser.objects.get(id=user.id)
    except WeUser.DoesNotExist:
        return False
    return not we_user.is_tutor


def unauthorized(request):
    return render(request,"unauthorized.html")


def get_allowed_tiers(user_id):
    we_user = WeUser.objects.get(id=user_id)
    allowed_tiers = []
    if we_user.tier:
        if we_user.tier.label =='bronze':
            allowed_tiers = ['bronze']
        elif we_user.tier.label =='silver':
            allowed_tiers = ['silver','bronze']
        elif we_user.tier.label == 'gold':
            allowed_tiers = ['silver', 'bronze','gold']

    return allowed_tiers


@login_required
def student_home(request):
    we_user = WeUser.objects.get(id=request.user.id)
    course_list =  we_user.registered_courses.filter(is_published=True)
    course_list = course_list.annotate(is_enrolled=models.Exists(
        we_user.registered_courses.filter(pk=models.OuterRef('pk'))
    ))
    allowed_tiers = get_allowed_tiers(request.user.id)
    response = render(request, 'student_home.html', {'courses': course_list})
    response.set_cookie('allowed_tiers', allowed_tiers)
    return response


@login_required
def course(request, course_id):
    selected_course = Course.objects.get(id=course_id)
    we_user = WeUser.objects.get(id=request.user.id)
    selected_course.is_enrolled = we_user.registered_courses.filter(id=selected_course.id).exists()
    module_list = Module.objects.filter(course_id=course_id)
    is_locked = False
    for module in module_list:
        quiz = Quiz.objects.filter(module=module)
        module.is_passed = False
        if not quiz:
            module.is_passed = True
        elif QuizAttempt.objects.filter(quiz__id=quiz[0].id, user__id=we_user.id):
            module.is_passed = QuizAttempt.objects.get(quiz=quiz[0], user=we_user).is_passed
        module.is_locked = is_locked
        if not module.is_passed:
            is_locked = True
    return render(request, 'course.html', {'course': selected_course, 'modules': module_list})


@login_required
def profile(request):
    try:
        we_user = WeUser.objects.get(id=request.user.id)
        student_count = Course.objects.filter(tutor=we_user).aggregate(student_count=Count('registered_users'))['student_count']
    except WeUser.DoesNotExist:
        return False

    print(we_user)

    return render(request, 'profile.html', {'student_count': student_count})

@login_required
@user_passes_test(tutor_check, login_url="/unauth")
def tutor_home(request):
    # POST for course creation/

    if request.method == 'GET':
        course_list = Course.objects.filter(tutor_id=request.user.id)
        categories = Category.objects.all()

        return render(request, 'tutor_courses.html', {'courses': course_list, 'categories': categories})

@login_required
@user_passes_test(tutor_check,login_url="/unauth")
def tutor_course(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        if course_form.is_valid():
            course = course_form.save(commit=False)
            tier = Tier.objects.get(label=course_form.cleaned_data['tier_name'])
            category = Category.objects.get(id=course_form.cleaned_data['category_id'])
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
        we_user = WeUser.objects.get(id=request.user.id)
        course = Course.objects.get(id=course_id);
        modules = list(course.modules.all())
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


@login_required
@user_passes_test(tutor_check,login_url="/unauth")
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
                    allowed_tiers = get_allowed_tiers(request.user.id)
                    response = HttpResponseRedirect(reverse('welearn:student_home'))
                    response.set_cookie('allowed_tiers',allowed_tiers)
                    return response
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
            for question in quiz.questions.all():
                selected_option_id = form.cleaned_data[f'question_{question.id}']
                selected_option = get_object_or_404(Option, pk=selected_option_id)
                if selected_option.is_correct:
                    score += 1

            # Save the quiz attempt and score for the current user
            we_user = WeUser.objects.get(id=request.user.id)
            quiz_attempt, created = QuizAttempt.objects.get_or_create(user=we_user, quiz=quiz)
            quiz_attempt.score = score
            quiz_attempt.max_score = quiz.questions.count()
            percent = (quiz_attempt.score * 100)/quiz_attempt.max_score
            if percent >= quiz_attempt.quiz.grade_required:
                quiz_attempt.is_passed = True
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
    percent = (quiz_attempt.score/quiz_attempt.max_score)*100
    pass_value = False
    if percent >= quiz.grade_required:
        pass_value = True
    return render(request, 'quiz_result.html', {'quiz': quiz, 'score': quiz_attempt.score, 'pass_value':pass_value, 'percent':percent})



class AddContent(View):

    @method_decorator(login_required)
    @method_decorator(user_passes_test(tutor_check, login_url="/unauth"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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


class DeleteQuiz(View):
    def delete(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        quiz.delete()
        return HttpResponse(status=204)


@login_required
@user_passes_test(student_check,login_url="/unauth")
def search(request):
    query = request.GET['query']
    we_user = WeUser.objects.get(id=request.user.id)
    allowed_tiers = get_allowed_tiers(request.user.id)
    course_search = Course.objects.filter(Q(tags__contains=query) | Q(title__contains=query)).filter(is_published=True);
    course_search = course_search.annotate(is_enrolled=models.Exists(
        we_user.registered_courses.filter(pk=models.OuterRef('pk'))
    ))
    response = render(request,'search.html',{'courses':course_search,'search_query':query})
    response.set_cookie('allowed_tiers', allowed_tiers)

    return response;


class EnrollCourse(View):
    def post(self, request, course_id):
        print("1")
        we_user = WeUser.objects.get(id=request.user.id)
        enroll_course = get_object_or_404(Course, id=course_id)
        allowed_tiers = get_allowed_tiers(request.user.id);
        print("2")
        if enroll_course.tier and enroll_course.tier.label in allowed_tiers:
            enroll_course.registered_users.add(we_user)
            return HttpResponseRedirect(reverse("welearn:course", kwargs={'course_id': course_id}))
        else:
            print("3")
            return HttpResponse(status=400)


class CourseDashboard(View):

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if course.tutor.id != request.user.id:
            return HttpResponse(status=400)
        return render(request, "course_dash.html", {"course": course})


class CourseProgress(View):
    def get(self, request, course_id, student_id):
        course = get_object_or_404(Course, id=course_id)
        if course.tutor.id != request.user.id:
            return HttpResponse(status=400)
        module_list = course.modules.all()
        we_user = WeUser.objects.get(id=student_id)

        for module in module_list:
            quiz = Quiz.objects.filter(module=module)
            module.is_passed = False
            module.has_quiz = True
            module.given_quiz = False
            module.score = 0
            module.max_score = 0
            module.percent = 0
            module.required_percent = 0

            if not quiz:
                module.is_passed = True
                module.has_quiz = False
            else:
                module.required_percent = quiz[0].grade_required
                module.max_score = quiz[0].questions.count()

            if module.has_quiz and QuizAttempt.objects.filter(quiz__id=quiz[0].id, user__id=student_id):
                qa = QuizAttempt.objects.get(quiz=quiz[0], user__id=student_id)
                module.given_quiz = True
                module.score = qa.score
                module.max_score = qa.max_score
                module.percent = (module.score * 100)/module.max_score
                module.is_passed = qa.is_passed
        return render(request, "student_progress.html", {"course":course, "modules":module_list, "student":we_user})



@login_required
@user_passes_test(student_check,login_url="/unauth")
def billing_page(request):
    we_user = WeUser.objects.get(id=request.user.id)
    if request.method == 'POST':

        if we_user.tier and we_user.tier.label == 'gold':
            return HttpResponseForbidden("Gold Tier users has  no option to upgrade")

        tname = request.GET.get("tier", "bronze")
        tier = get_object_or_404(Tier, label=tname)
        form = BillingInfoForm(request.POST)
        if form.is_valid():
            # Save the form to the database
            bi = form.save()
            return redirect(reverse('welearn:payment_page') + f"?bi_id={bi.id}")
    else:
        tname = request.GET.get("tier", "bronze")
        tier = get_object_or_404(Tier, label=tname)
        cname = request.user.first_name + " " + request.user.last_name
        amount = tier.price
        if we_user.tier:
            amount = amount - we_user.tier.price
        data = {'amount':amount,'customer_name': cname, 'email': request.user.email}
        form = BillingInfoForm(data)
        return render(request, 'billing.html', {'form': form, "tier": tier})


# In views.py

@login_required
@user_passes_test(student_check,login_url="/unauth")
def payment_page(request):
    if request.method == 'POST':
        instance  = UserBillingInfo.objects.get(id=request.GET["bi_id"])
        payment_form = PaymentForm(request.POST, instance=instance)
        if payment_form.is_valid():
            is_payment_successful, error_message = validate_payment(payment_form.cleaned_data)
            if is_payment_successful:
                payment_form.save()
                we_user = request.we_user
                we_user.tier = instance.tier
                we_user.save()
                return redirect(reverse('welearn:success_page') + f"?tx_id={instance.transaction_id}")
            else:
                return HttpResponseRedirect(f'/payment/fail/?error_message={error_message}')
    else:
        bi_id = request.GET.get("bi_id", None)
        if not bi_id:
            return HttpResponseRedirect(f'/payment/fail/?error_message=SomethingWentWrong')
        bi=get_object_or_404(UserBillingInfo, id=bi_id)
        payment_form = PaymentForm(instance=bi)
        tier = bi.tier
    return render(request, 'payment.html', {'form': payment_form, 'bi_id': bi_id, "tier": tier})

# Payment success page view function
def success_page(request):
    return render(request, 'payment_success.html', {'tx_id': request.GET['tx_id']})


@user_passes_test(student_check,login_url="/unauth")
def payment_fail_page(request):
    error_message = request.GET.get('error_message')
    return render(request, 'payment_fail.html', {'error_message': error_message})

def validate_payment(payment_data):
    card_number = payment_data.get('card_number')
    expiry_date = payment_data.get('expiry_date')
    cvv = payment_data.get('cvv')

    # Check card number is 10 digits
    if card_number and not re.match(r'^\d{16}$', card_number):
        error_message = 'Card number must be 10 digits.'
        return False, error_message


    # Check expiry date format is MMYYYY
    if expiry_date and not re.match(r'^\d{6}$', expiry_date):
        error_message = 'Expiry date format is MMYYYY.'
        return False, error_message

    # Extract expiry_month and expiry_year from expiry_date
    expiry_month = int(expiry_date[:2])
    expiry_year = int(expiry_date[2:])

    # Check if expiry date is less than today
    today = date.today()
    if expiry_year < today.year or (expiry_year == today.year and expiry_month < today.month):
        error_message = 'Card has expired.'
        return False, error_message

    # Check CVV number is 3 digits
    if cvv and not re.match(r'^\d{3}$', cvv):
        error_message = 'CVV number must be 3 digits.'
        return False, error_message

    # All validations passed, payment is successful
    return True, None


def calculate_total_amount_based_on_currency(currency):
    # Replace this with your custom logic to calculate the total amount based on currency exchange rates or other relevant factors.
    # For demonstration purposes, let's assume a fixed rate for each currency.
    currency_rates = {
        'IND': 75.0,  # 1 INR = 75.0 USD
        'USD': 1.0,  # 1 USD = 1.0 USD
        'AUD': 0.75,  # 1 AUD = 0.75 USD
        'CAD': 0.80,  # 1 CAD = 0.80 USD
        'GER': 0.90,  # 1 GER = 0.90 USD
        'EUR': 0.85,  # 1 EUR = 0.85 USD
    }

    # Let's assume the total amount is 100 USD for demonstration purposes
    total_amount_usd = 100.0

    # Calculate the total amount based on the selected currency
    total_amount = total_amount_usd / currency_rates[currency]

    # Round the total_amount to two decimal places
    return round(total_amount, 2)


def calculate_total_amount(currency):
    # Implement the logic to calculate the total amount based on the selected currency
    # For demonstration purposes, let's assume you have a fixed rate for each currency
    currency_rates = {
        'IND': 75.0,  # 1 INR = 75.0 USD
        'USD': 1.0,  # 1 USD = 1.0 USD
        'AUD': 0.75,  # 1 AUD = 0.75 USD
        'CAD': 0.80,  # 1 CAD = 0.80 USD
        'GER': 0.90,  # 1 GER = 0.90 USD
        'EUR': 0.85,  # 1 EUR = 0.85 USD
    }

    # Let's assume the total amount is 100 USD for demonstration purposes
    total_amount_usd = 100.0

    # Calculate the total amount based on the selected currency
    total_amount = total_amount_usd / currency_rates[currency]

    # Round the total_amount to two decimal places
    return round(total_amount, 2)



@login_required
def mail(request):
    if request.method == 'POST':
        form = MailForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user']
            message = form.cleaned_data['message']
            curr_user = WeUser.objects.get(pk=request.user.id)
            to_user = WeUser.objects.get(pk=user_id)
            current_time = datetime.now()
            m = Mail()
            m.message = message
            m.from_user = curr_user
            m.to_user = to_user
            m.msg_time = current_time
            m.save()
            return redirect('welearn:my_messages')
    else:
        form = MailForm()
        if request.GET and request.GET['user_id']:
            form = MailForm(initial={'user':request.GET['user_id']})
    return render(request, 'mail.html', {'form': form})


@login_required
def my_messages(request, *args, **kwargs):
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            curr_user = WeUser.objects.get(pk=request.user.id)
            usr_id = request.POST.get('to_user', None)
            to_user = WeUser.objects.get(pk=usr_id)
            current_time = datetime.now()
            m = Mail()
            m.message = message
            m.from_user = curr_user
            m.to_user = to_user
            m.msg_time = current_time
            m.save()

    msgs = Mail.objects.filter(Q(from_user=request.user.id) | Q(to_user=request.user.id)).order_by('-msg_time')

    from_users = Mail.objects.values_list('from_user', flat=True).distinct()
    to_users = Mail.objects.values_list('to_user', flat=True).distinct()

    individual_users_set = set(from_users) | set(to_users)
    individual_users_set.discard(request.user.id)

    threads = {}
    for usr in individual_users_set:
        for m in msgs:
            if (m.to_user.id == request.user.id and m.from_user.id == usr) or (
                    m.to_user.id == usr and m.from_user.id == request.user.id):
                if(usr in threads.keys()):
                    threads[usr].append(m)
                else:
                    threads[usr] = [m]
    conv = [list(value) for value in threads.values()]
    form = ReplyForm()

    return render(request, 'view_messages.html', {'messages_list': conv, 'form':form})


def generate_certificate(background_image, user_name, course_name, completion_date, certified_by):
    # Load the custom cursive font
    cursive_font_path = "media/Pacifico-Regular.ttf"
    pdfmetrics.registerFont(TTFont("CursiveFont", cursive_font_path))

    # Create a BytesIO buffer to store the PDF in-memory
    buffer = BytesIO()

    # Create a canvas with the given background image and save it to the buffer
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    c.drawImage(background_image, 0, 0, width=landscape(letter)[0], height=landscape(letter)[1])

    # Set font and font size for the text (use the custom cursive font)
    c.setFont("CursiveFont", 36)

    # Get the text width and height for the main course name text
    text_width = c.stringWidth(course_name, "CursiveFont", 36)
    text_height = 36

    # Calculate the coordinates to center the main course name text on the page
    x = (landscape(letter)[0] - text_width) / 2
    y = (landscape(letter)[1] - text_height) / 2

    y = y  + 50

    # Draw the main course name text on the certificate
    c.drawString(x, y, course_name)

    # Split the "This is to certify..." line into two lines
    certify_text_line1 = f"This is to certify that {user_name} has completed"
    certify_text_line2 = f"the course \"{course_name}\""

    # Calculate the y-coordinate for each line
    certify_line1_y = y - 50
    certify_line2_y = certify_line1_y - 30
    # Add "This is to certify..." text lines to the certificate
    c.setFont("CursiveFont", 18)
    l1_width = c.stringWidth(certify_text_line1, "CursiveFont", 18)
    l1x = (landscape(letter)[0] - l1_width) / 2
    c.drawString(l1x, certify_line1_y, certify_text_line1)
    l2_width = c.stringWidth(certify_text_line2, "CursiveFont", 18)
    l2x = (landscape(letter)[0] - l2_width) / 2
    c.drawString(l2x, certify_line2_y, certify_text_line2)



    # Add "Certified by" text and name
    certified_by_y = certify_line2_y - 50
    c.setFont("CursiveFont", 18)
    certified_by_text = f"Certified by {certified_by}"
    certified_by_width = c.stringWidth(certified_by_text, "CursiveFont", 18)
    x_certified_by = (landscape(letter)[0] - certified_by_width) / 2
    c.drawString(x_certified_by, certified_by_y, certified_by_text)

    # Add completion date below the course name
    completion_date_y = certified_by_y - 23
    c.setFont("CursiveFont", 18)
    completion_date_text = f"on {completion_date}"
    completion_date_width = c.stringWidth(completion_date_text, "CursiveFont", 18)
    x_completion_date = (landscape(letter)[0] - completion_date_width) / 2
    c.drawString(x_completion_date, completion_date_y, completion_date_text)

    # Save the canvas to the buffer
    c.save()

    # Reset the buffer position to the beginning
    buffer.seek(0)

    return buffer

@login_required()
@user_passes_test(student_check,login_url="/unauth")
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    user_name = request.user.first_name
    course_name = course.title
    dtime = datetime.now()
    format_string = "%B %d, %Y"
    completion_date = dtime.strftime(format_string)
    certified_by = "WeLearn"

    # Path to the background image (change this to your actual background image path)
    background_image = "media/cert-background.png"

    # Generate the certificate in-memory
    buffer = generate_certificate(background_image, user_name, course_name, completion_date, certified_by)

    # Send the generated certificate as a downloadable response
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate.pdf"'

    return response