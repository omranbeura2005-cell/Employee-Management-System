import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_main.settings')

import django

django.setup()

from datetime import date
from django.contrib.auth import get_user_model
from employees.models import Department, Employee

User = get_user_model()

rows = [
    ('Aarav', 'Sharma', 'aarav.sharma', 'aarav.sharma@example.com', 'Software Engineer', 85000, 'Technology', 'Bengaluru', True),
    ('Ishita', 'Patel', 'ishita.patel', 'ishita.patel@example.com', 'HR Manager', 92000, 'Human Resources', 'Mumbai', True),
    ('Rohan', 'Iyer', 'rohan.iyer', 'rohan.iyer@example.com', 'Product Analyst', 72000, 'Product', 'Chennai', True),
    ('Meera', 'Nair', 'meera.nair', 'meera.nair@example.com', 'Finance Executive', 68000, 'Finance', 'Kochi', True),
    ('Vivaan', 'Gupta', 'vivaan.gupta', 'vivaan.gupta@example.com', 'QA Engineer', 64000, 'Technology', 'Pune', True),
    ('Ananya', 'Reddy', 'ananya.reddy', 'ananya.reddy@example.com', 'UX Designer', 76000, 'Design', 'Hyderabad', True),
    ('Kabir', 'Singh', 'kabir.singh', 'kabir.singh@example.com', 'Sales Executive', 58000, 'Sales', 'New Delhi', True),
    ('Diya', 'Verma', 'diya.verma', 'diya.verma@example.com', 'Operations Coordinator', 53000, 'Operations', 'Jaipur', False),
]

for first_name, last_name, username, email, designation, salary, department_name, location, is_active in rows:
    department, _ = Department.objects.get_or_create(
        name=department_name,
        defaults={'location': location},
    )
    user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
    user.email = email
    user.set_password('Welcome@2026')
    user.save()
    Employee.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'designation': designation,
            'salary': salary,
            'joining_date': date(2024, 6, 3),
            'is_active': is_active,
            'department': department,
            'user': user,
        },
    )

print('Indian employee seed complete.')
