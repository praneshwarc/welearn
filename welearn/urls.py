from django.urls import path
from . import views
from .views import AddContent, ContentView, DeleteQuiz

app_name = 'welearn'
urlpatterns = [
    path('', views.student_home, name='student_home'),
    path('home/', views.student_home, name='student_home'),
    path('courses/<int:course_id>/', views.course, name='course'),
    path('tutor/', views.tutor_home, name='tutor_home'),
    path('tutor/home/', views.tutor_home, name='tutor_home'),
    path('tutor/course/<int:course_id>/', views.tutor_course_id, name='tutor_course_id'),
    path('tutor/course/<int:course_id>/modules/', views.tutor_modules, name='tutor_modules'),
    path('tutor/module/<int:module_id>/', views.tutor_module_id, name="tutor_module_id"),
    path('login/', views.login_view, name="login"),
    path('signup/', views.sign_up, name="signup"),
    path('logout/', views.logout_view, name="logout"),
    path('quiz/<int:module_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz_result/<int:module_id>/', views.quiz_result, name='quiz_result'),
    path('profile/', views.profile, name='profile'),
    path('tutor/module/<int:module_id>/content', AddContent.as_view(), name="add_content"),
    path('tutor/content/<int:content_id>/', ContentView.as_view(), name="delete_content"),
    path('tutor/module/<int:module_id>/create_quiz/', views.create_quiz, name='create-quiz'),
    path('tutor/quiz/<int:quiz_id>/', DeleteQuiz.as_view(), name = 'delete_quiz')
]
