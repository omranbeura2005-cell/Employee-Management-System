from django.shortcuts import render , get_object_or_404 ,redirect
from .models import Employee # use to fetch the data from employee table to details page
from .forms import EmployeeForm
from django.contrib.auth.decorators import login_required


# Create your views here.


@login_required
def employee_detail(request, id):

    # Fetch the employee object based on the provided ID
    employee = get_object_or_404(Employee, id=id)
    print(employee)
    context = {
        'emp': employee
    }
    return render(request , 'employee_detail.html', context)


@login_required
def add_Employee(request):
    if request.method == 'POST':
        print(request.POST)
        form = EmployeeForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
        else :
            print(form.errors)
            
    form = EmployeeForm()
    context = {
        'form' : form
    }
    return render(request, 'add_employee.html', context)



@login_required
def edit_Employee(request, id):
    # Get the employee object from database using ID
    # If not found → show 404 error page
    employee = get_object_or_404(Employee, id=id)
    # Check if form is submitted (POST request)
    if request.method == 'POST':
        # Create form with submitted data + uploaded files
        # instance=employee → VERY IMPORTANT (update existing record, not create new)
        form = EmployeeForm(request.POST, request.FILES, instance=employee)   

        # Validate form data
        if form.is_valid():
            # Save updated data to database
            form.save()

            # Import Django messages framework
            from django.contrib import messages
            # Store success message (will be shown on next page)
            messages.success(request, "Employee updated successfully!")
            # Redirect to employee detail page after update
            # Prevents duplicate form submission
            return redirect('employee_detail', id=employee.id)
        
    else:
        # If request is GET → load form with existing employee data
        form = EmployeeForm(instance=employee)
    # Render edit page and send form to template
    return render(request, 'edit_employee.html', {'form': form})



