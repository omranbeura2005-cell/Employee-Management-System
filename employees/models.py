from django.conf import settings
from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name } - {self.location}"

class Employee(models.Model):
    first_name = models.CharField(max_length =30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique = True)
    designation = models.CharField(max_length = 50)
    image = models.ImageField (upload_to = "emp_images",default = "default.png")
    salary = models.IntegerField()
    joining_date = models.DateField()
    is_active = models.BooleanField(default = True)
    department = models.ForeignKey(Department,on_delete = models.SET_NULL,blank = True,null = True)
    manager = models.ForeignKey("self",on_delete = models.SET_NULL ,blank = True , null = True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='employee_profile')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    checked_in_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='attendance', blank=True, null=True)

    class Meta:
        ordering = ['-checked_in_at']


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('attendance', 'Attendance'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='audit_logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    before_data = models.JSONField(default=dict, blank=True)
    after_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class AdminChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']



