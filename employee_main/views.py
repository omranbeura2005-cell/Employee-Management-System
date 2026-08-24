from django.http import HttpResponse
from employees.models import Employee #responsible to fetch the data from employee table in home page
from django.shortcuts import render


def home(request):

    # Fetch the data from employee tables
    employees = Employee.objects.all()
    context = {
        'employees':employees
        #'emp' :emploues also true 
    }


    return render(request, 'home.html',context)

