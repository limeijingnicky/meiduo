from users import views
from django.urls import path

urlpatterns = [
    path(r'register/', views.RegisterView.as_view()),
]
