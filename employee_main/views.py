from django.contrib.auth.decorators import login_required
from employees.models import Employee #responsible to fetch the data from employee table in home page
from django.shortcuts import render


@login_required
def home(request):

    # Fetch the data from employee tables
    employees = Employee.objects.all()
    context = {
        'employees': employees,
        'can_manage': request.user.is_staff,
    }


    return render(request, 'home.html',context)

