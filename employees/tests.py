from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AdminChatMessage, Attendance, AuditLog, Employee


class EmployeeAccessTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.admin = user_model.objects.create_user('admin', password='admin-pass', is_staff=True)
		self.employee_user = user_model.objects.create_user('worker', password='worker-pass')
		self.other_user = user_model.objects.create_user('other', password='other-pass')
		self.employee = Employee.objects.create(
			first_name='Jane', last_name='Doe', email='jane@example.com',
			designation='Engineer', salary=50000, joining_date='2026-01-01',
			user=self.employee_user,
		)

	def test_anonymous_user_is_sent_to_login(self):
		response = self.client.get(reverse('home'))
		self.assertRedirects(response, f'{reverse("login")}?next={reverse("home")}')

	def test_employee_can_view_but_cannot_manage(self):
		self.client.login(username='worker', password='worker-pass')
		self.assertEqual(self.client.get(reverse('home')).status_code, 200)
		self.assertEqual(self.client.get(reverse('add_Employee')).status_code, 302)
		self.assertEqual(self.client.post(reverse('delete_employee', args=[self.employee.id])).status_code, 302)
		self.assertTrue(Employee.objects.filter(pk=self.employee.pk).exists())

	def test_admin_can_delete_employee(self):
		self.client.login(username='admin', password='admin-pass')
		warning = self.client.get(reverse('delete_employee', args=[self.employee.id]))
		self.assertContains(warning, 'Delete employee?')
		response = self.client.post(reverse('delete_employee', args=[self.employee.id]))
		self.assertRedirects(response, reverse('home'))
		self.assertFalse(Employee.objects.filter(pk=self.employee.pk).exists())

	def test_admin_sees_edit_warning_before_form(self):
		self.client.login(username='admin', password='admin-pass')
		response = self.client.get(reverse('edit_Employee', args=[self.employee.id]))
		self.assertContains(response, 'Edit employee?')
		self.assertNotContains(response, 'Update Employee')

	def test_employee_can_only_check_in_for_self(self):
		self.client.login(username='other', password='other-pass')
		response = self.client.post(reverse('attendance_check_in', args=[self.employee.id]))
		self.assertEqual(response.status_code, 403)
		self.assertEqual(Attendance.objects.count(), 0)

		self.client.login(username='worker', password='worker-pass')
		response = self.client.post(reverse('attendance_check_in', args=[self.employee.id]))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Attendance.objects.count(), 1)
		self.assertEqual(AuditLog.objects.filter(action='attendance').count(), 1)

	def test_admin_insights_and_chat_are_admin_only_and_saved(self):
		self.client.login(username='worker', password='worker-pass')
		self.assertEqual(self.client.get(reverse('admin_insights')).status_code, 302)

		self.client.login(username='admin', password='admin-pass')
		response = self.client.get(reverse('admin_insights'), {'status': 'active'})
		self.assertEqual(response.status_code, 200)
		response = self.client.post(reverse('admin_chat'), {'question': 'How many attendance check-ins?'})
		self.assertRedirects(response, reverse('admin_insights'))
		self.assertEqual(AdminChatMessage.objects.count(), 1)
		self.assertIn('Jane Doe', AdminChatMessage.objects.first().answer)

	def test_chat_says_when_question_is_unsupported_and_suggests_capabilities(self):
		self.client.login(username='admin', password='admin-pass')
		self.client.post(reverse('admin_chat'), {'question': 'What is the weather today?'})
		message = AdminChatMessage.objects.get()
		self.assertIn('I cannot answer that yet.', message.answer)
		self.assertIn('attendance', message.answer)

	def test_chat_reports_deleted_employee_from_audit_log(self):
		self.client.login(username='admin', password='admin-pass')
		self.client.post(reverse('delete_employee', args=[self.employee.id]))
		self.client.post(reverse('admin_chat'), {'question': 'Which employee was deleted?'})
		message = AdminChatMessage.objects.get()
		self.assertIn('Jane Doe', message.answer)

	def test_employee_edit_saves_before_and_after_snapshots(self):
		self.client.login(username='admin', password='admin-pass')
		response = self.client.post(reverse('edit_Employee', args=[self.employee.id]) + '?confirm=1', {
			'first_name': 'Janet',
			'last_name': 'Doe',
			'email': 'jane@example.com',
			'designation': 'Senior Engineer',
			'salary': 60000,
			'joining_date': '2026-01-01',
			'is_active': 'on',
			'username': 'worker',
		})
		self.assertEqual(response.status_code, 302)
		log = AuditLog.objects.get(action='updated')
		self.assertEqual(log.before_data['name'], 'Jane Doe')
		self.assertEqual(log.after_data['name'], 'Janet Doe')
		self.assertIsNotNone(log.created_at)

	def test_duplicate_employee_username_returns_form_error(self):
		self.client.login(username='admin', password='admin-pass')
		response = self.client.post(reverse('add_Employee'), {
			'first_name': 'Rahul',
			'last_name': 'Kumar',
			'email': 'rahul@example.com',
			'designation': 'Developer',
			'salary': 70000,
			'joining_date': '2026-01-01',
			'is_active': 'on',
			'username': ' WORKER ',
			'password': 'new-pass',
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'That username is already in use.')

# Create your tests here.
