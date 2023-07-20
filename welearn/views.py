from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from .models import Course, Module


def homepage(request):
    course_list = Course.objects.all()
    return render(request, 'homepage.html', {'courses': course_list})


def course(request, course_id):
    selected_course = Course.objects.get(id=course_id)
    module_list = Module.objects.filter(course_id=course_id)
    module = module_list[1]
    print(module.contents.all()[0].file)
    return render(request, 'course_home.html', {'course': selected_course, 'modules': module_list})


def tutor_check(user):
    try:
        we_user = WeUser.objects.get(id=user.id)
    except WeUser.DoesNotExist:
        return False
    return we_user.is_tutor


# @user_passes_test(tutor_check)
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



# @user_passes_test(tutor_check)
def tutor_modules(request, course_id):
    course = Course.objects.get(id=course_id);
    modules = course.modules.all()

    return render(request, "tutor_modules.html", {'course': course, 'modules': modules})
