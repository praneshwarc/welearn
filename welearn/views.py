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
    print(user.groups.all())
    if user.groups:
        return 'tutor' in user.groups.all()
    else:
        return True


# @user_passes_test(tutor_check)
def tutor_courses(request):
    course_list = [{
        'id': 1,
        'title': 'Introduction to Python',
        'description': 'This is a course to learn python from scratch',
        'category': {
            "id": 1,
            "value": "Technology"
        },
        'tags': 'python technology programming coding',
        'duration': {
            'hours': 2,
            'minutes': 20
        },
        'tier': 'silver',
        'is_published': True
    },
        {
            'id': 2,
            'title': 'Introduction to Python',
            'description': 'This is a course to learn python from scratch',
            'category': {
                "id": 1,
                "value": "Technology"
            },
            'tags': 'python technology programming coding',
            'duration': {
                'hours': 2,
                'minutes': 20
            },
            'tier': 'bronze',
            'is_published': False
        },
        {
            'id': 3,
            'title': 'Introduction to Python',
            'description': 'This is a course to learn python from scratch',
            'category': {
                "id": 1,
                "value": "Technology"
            },
            'tags': 'python technology programming coding',
            'duration': {
                'hours': 1,
                'minutes': 20
            },
            'tier': 'gold',
            'is_published': True
        }
    ]
    categories = [
        {
            'id': 1,
            'value': 'Business',
            'tokens': 'business organization company'
        },
        {
            'id': 2,
            'value': 'Human Resources',
            'tokens': 'hr human resources talent employee'
        },
        {
            'id': 3,
            'value': 'Finance & Accounting',
            'tokens': 'finance wealth company accounting'
        },
        {
            'id': 4,
            'value': 'Technology',
            'tokens': 'programming technology coding development'
        },
        {
            'id': 5,
            'value': 'Project Management',
            'tokens': 'project product organization agile sprint'
        }
    ]
    course_list = Course.objects.all()
    print(course_list[0].tier)

    return render(request, 'tutor_courses.html', {'courses': course_list, 'categories': categories, 'edit': True})


# @user_passes_test(tutor_check)
def tutor_modules(request, course_id):
    course = Course.objects.get(id=course_id);
    modules = course.modules.all()

    return render(request, "tutor_modules.html", {'course': course, 'modules': modules})
