from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db.models import Count
from django.shortcuts import render , get_object_or_404 ,redirect
from django.views.decorators.http import require_POST
from .models import AdminChatMessage, Attendance, AuditLog
from .models import Employee # use to fetch the data from employee table to details page
from .forms import EmployeeForm


# Create your views here.


def admin_required(view):
    return user_passes_test(lambda user: user.is_staff, login_url='home')(view)


def employee_snapshot(employee):
    return {
        'name': employee.full_name(),
        'email': employee.email,
        'designation': employee.designation,
        'salary': employee.salary,
        'joining_date': employee.joining_date.isoformat(),
        'is_active': employee.is_active,
        'department': str(employee.department) if employee.department else '',
        'manager': str(employee.manager) if employee.manager else '',
        'username': employee.user.username if employee.user_id else '',
    }


def assistant_answer(question):
    lowered = question.casefold()
    employees = Employee.objects.annotate(attendance_count=Count('attendance'))
    suggestions = 'Try: "How many attendance check-ins?", "Who is inactive?", "What is the average salary?", or "Which employees were deleted?"'

    if not question:
        return f'Please enter a question. {suggestions}'
    if any(word in lowered for word in ('help', 'what can you', 'what do you do', 'suggest')):
        return f'I can summarize attendance, count active or inactive employees, calculate average salary, and list audited changes. {suggestions}'
    if any(word in lowered for word in ('deleted', 'delete', 'removed', 'remove')):
        deleted = AuditLog.objects.filter(action='deleted').order_by('-created_at')
        if not deleted.exists():
            return 'No deleted employee records have been saved in the audit log.'
        return 'Deleted employees: ' + '; '.join(
            f"{log.before_data.get('name', 'Unknown')} at {log.created_at.strftime('%b %d, %Y %I:%M %p')}"
            for log in deleted[:20]
        )
    if any(word in lowered for word in ('change', 'edited', 'updated', 'created')):
        logs = AuditLog.objects.select_related('employee').order_by('-created_at')[:10]
        if not logs:
            return 'No employee changes have been saved in the audit log.'
        return 'Recent changes: ' + '; '.join(
            f'{log.get_action_display()} {log.employee.full_name() if log.employee else log.before_data.get("name", "employee")} '
            f'on {log.created_at.strftime("%b %d, %Y %I:%M %p")}'
            for log in logs
        )
    if any(word in lowered for word in ('attendance', 'present', 'check-in', 'check in')):
        return '; '.join(f'{employee.full_name()}: {employee.attendance_count} attendance(s)' for employee in employees) or 'No employee attendance records found.'
    if 'inactive' in lowered:
        names = ', '.join(employee.full_name() for employee in employees.filter(is_active=False))
        return f'Inactive employees: {names or "none"}.'
    if 'active' in lowered:
        return f'There are {employees.filter(is_active=True).count()} active employees.'
    if any(word in lowered for word in ('salary', 'pay', 'income')):
        return f'The average salary is {sum(employee.salary for employee in employees) / employees.count():.0f}.' if employees.exists() else 'No salary data found.'
    if any(word in lowered for word in ('how many', 'count', 'number')) and 'employee' in lowered:
        return f'There are {employees.count()} employees.'
    return f'I cannot answer that yet. I only answer questions about employee counts, attendance, active or inactive staff, salary, and saved changes. {suggestions}'


@admin_required
def admin_insights(request):
    employees = Employee.objects.select_related('department').annotate(attendance_count=Count('attendance'))
    status = request.GET.get('status', '')
    employee_id = request.GET.get('employee', '')
    action = request.GET.get('action', '')
    if status == 'active':
        employees = employees.filter(is_active=True)
    elif status == 'inactive':
        employees = employees.filter(is_active=False)
    if employee_id:
        employees = employees.filter(id=employee_id)
    logs = AuditLog.objects.select_related('employee', 'actor')
    if employee_id:
        logs = logs.filter(employee_id=employee_id)
    if action:
        logs = logs.filter(action=action)
    return render(request, 'admin_insights.html', {
        'employees': employees,
        'logs': logs[:100],
        'all_employees': Employee.objects.order_by('first_name', 'last_name'),
        'selected_status': status,
        'selected_employee': employee_id,
        'selected_action': action,
        'chat_messages': AdminChatMessage.objects.filter(user=request.user)[:30],
    })


@admin_required
@require_POST
def admin_chat(request):
    question = request.POST.get('question', '').strip()
    answer = assistant_answer(question)
    AdminChatMessage.objects.create(user=request.user, question=question, answer=answer)
    return redirect('admin_insights')


@login_required
def employee_detail(request, id):

    # Fetch the employee object based on the provided ID
    employee = get_object_or_404(Employee, id=id)
    context = {
        'emp': employee,
        'can_view_sensitive': request.user.is_staff or employee.user_id == request.user.id,
        'can_check_in': request.user.is_staff or employee.user_id == request.user.id,
    }
    return render(request , 'employee_detail.html', context)


@admin_required
def add_Employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)

        if form.is_valid():
            employee = form.save()
            AuditLog.objects.create(employee=employee, actor=request.user, action='created', after_data=employee_snapshot(employee))
            messages.success(request, 'Employee added successfully.')
            return render(request, 'add_employee.html', {
                'form': EmployeeForm(),
                'employee_added': True,
            })
    else:
        form = EmployeeForm()
    context = {
        'form' : form
    }
    return render(request, 'add_employee.html', context)



@admin_required
def edit_Employee(request, id):
    # Get the employee object from database using ID
    # If not found → show 404 error page
    employee = get_object_or_404(Employee, id=id)
    if request.method == 'GET' and request.GET.get('confirm') != '1':
        return render(request, 'action_confirm.html', {
            'title': 'Edit employee?',
            'message': f'You are about to edit {employee.full_name()}.',
            'confirm_url': f'{request.path}?confirm=1',
            'confirm_label': 'Continue to edit',
            'confirm_by_post': False,
        })

    # Check if form is submitted (POST request)
    if request.method == 'POST':
        before_data = employee_snapshot(employee)
        # Create form with submitted data + uploaded files
        # instance=employee → VERY IMPORTANT (update existing record, not create new)
        form = EmployeeForm(request.POST, request.FILES, instance=employee)   

        # Validate form data
        if form.is_valid():
            # Save updated data to database
            employee = form.save()
            AuditLog.objects.create(employee=employee, actor=request.user, action='updated', before_data=before_data, after_data=employee_snapshot(employee))

            # Import Django messages framework
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


@admin_required
def delete_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == 'GET':
        return render(request, 'action_confirm.html', {
            'title': 'Delete employee?',
            'message': f'This will permanently delete {employee.full_name()}.',
            'confirm_url': request.path,
            'confirm_label': 'Delete employee',
            'danger': True,
            'confirm_by_post': True,
        })
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)
    before_data = employee_snapshot(employee)
    AuditLog.objects.create(employee=employee, actor=request.user, action='deleted', before_data=before_data)
    employee.delete()
    messages.success(request, 'Employee deleted successfully.')
    return redirect('home')


@login_required
@require_POST
def attendance_check_in(request, id):
    employee = get_object_or_404(Employee, id=id)
    if not request.user.is_staff and employee.user_id != request.user.id:
        return JsonResponse({'error': 'You can only check in for your own account.'}, status=403)
    attendance = Attendance.objects.create(employee=employee, photo=request.FILES.get('photo'))
    AuditLog.objects.create(employee=employee, actor=request.user, action='attendance', after_data={
        'attendance_id': attendance.id,
        'checked_in_at': attendance.checked_in_at.isoformat(),
    })
    return JsonResponse({'message': 'Attendance recorded.'})



