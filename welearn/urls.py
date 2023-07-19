from django.urls import path
from . import views

app_name = 'welearn'
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('home', views.homepage, name='homepage'),
    path('tutor/courses', views.tutor_courses, name='tutor_courses'),
    path('tutor/courses/<int:course_id>/modules', views.tutor_modules, name='tutor_modules')
]
