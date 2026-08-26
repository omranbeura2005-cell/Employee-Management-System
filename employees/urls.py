from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.employee_detail, name='employee_detail'),
    path('add/', views.add_Employee, name='add_Employee'),
    path('edit/<int:id>/', views.edit_Employee, name='edit_Employee'),
    path('delete/<int:id>/', views.delete_employee, name='delete_employee'),
    path('attendance/<int:id>/', views.attendance_check_in, name='attendance_check_in'),
    path('admin-insights/', views.admin_insights, name='admin_insights'),
    path('admin-chat/', views.admin_chat, name='admin_chat'),
]