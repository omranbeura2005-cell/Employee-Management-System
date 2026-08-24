from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.employee_detail, name='employee_detail'),
    path('add/', views.add_Employee, name='add_Employee'),
    path('edit/<int:id>/', views.edit_Employee, name='edit_Employee')
]