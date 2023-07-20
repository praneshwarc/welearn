from django.urls import path
from . import views

app_name = 'welearn'
urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('home', views.homepage, name='homepage'),
    path('courses/<int:course_id>/', views.course, name='course'),
    path('tutor/courses/', views.tutor_courses, name='tutor_courses'),
    path('tutor/courses/<int:course_id>/', views.tutor_courses_id, name='tutor_courses_id'),
    path('tutor/courses/<int:course_id>/modules/', views.tutor_modules, name='tutor_modules'),
    path('login/', views.login_view, name="login"),
    path('signup/', views.sign_up, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('quiz/<int:module_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz_result/<int:module_id>/', views.quiz_result, name='quiz_result'),
    path('profile/', views.profile, name='profile'),
]
