from django.contrib import admin
from .models import (Assignment, AttendanceMonitor, AttendanceRecord, ClassLevel, Classe, ContactAddress,
	ContactStudent, Contact, EducationLevel, EnrollmentRecord, Gradebook, Parent, ParentAddress, SubjectInstance,
	StudAddress, StudentAttendance, StudentParent, Student, TeacherEnrollment, Teacher)

from django.contrib.admin import AdminSite
# # Register your models here.

admin.site.register(EducationLevel)
admin.site.register(ClassLevel)

#admin.site.register(SubjectInstance)


class EventAdminSite(admin.AdminSite):
    site_header = "Daandi School Site"
    site_title = "Department Heads"
    index_title = "Welcome to Department Head Portal"


event_admin_site = EventAdminSite(name='departments')
event_admin_site.register(SubjectInstance)
"""
"""

class StudentsInline(admin.TabularInline):
	model = Student
	fields = ('user','stud_id','first_name','last_name','level','phone')
	readonly_fields = ('stud_id','first_name','last_name','level')

class TeachersInline(admin.TabularInline):
	model = Teacher
	fields = ('t_id','is_monitor','first_name','last_name','dob','employed_at','education_level','phone')
	readonly_fields = ('user','t_id','is_monitor','first_name','last_name','dob','employed_at','education_level')

class ClassesInline(admin.TabularInline):
	model = Classe
	fields = ('class_id','description','start_date','end_date','class_url','level','completed')
	readonly_fields = ('class_id','description','start_date','end_date','class_url','level','completed')

class TeacherEnrollmentInline(admin.TabularInline):
	model = TeacherEnrollment
	fields = ('subj_field','teach_start','class_start','class_end','grade_due')
	#readonly_fields = ('subj_field',) 

class EnrollmentInline(admin.TabularInline):
	model = EnrollmentRecord
	fields = ('student','first_name','last_name','enrollment_start','enrollment_end')
	readonly_fields = ('student','first_name','last_name')

class AssignmentInline(admin.TabularInline):
	model = Assignment
	fields = ('assign_id','subject_field','description','assignment_date')
	readonly_fields = ('assign_id','subject_field')

class GradebookInline(admin.TabularInline):
	model = Gradebook
	fields = ('assign','student','submitted','graded_on','total','score')
	readonly_fields = ('assign','student_name','submitted','graded_on','total')

class ContactInline(admin.TabularInline):
	model = Contact
	readonly_fields = ('first_name','last_name','phone','email','phone')

class ContactStudentInline(admin.TabularInline):
	model = ContactStudent
	extra = 1

class ContactAddressInline(admin.TabularInline):
	model = ContactAddress
	readonly_fields = ('street','apt_no','city','region','country_code')

class AttendanceRecordInline(admin.TabularInline):
	model = AttendanceRecord
	fields = ('class_field','entry_count','monitor_name','session_date')
	readonly_fields = ('class_field','entry_count','monitor_name','session_date')

class StudAddressInline(admin.TabularInline):
	model = StudAddress
	fields = ('street','apt_no','city','region','country_code')

class StudentAttendanceInline(admin.TabularInline):
	model = StudentAttendance
	fields = ('session','student','attended')
	readonly_fields = ('session','student')

class SubjectInstancesInline(admin.TabularInline):
	model = SubjectInstance
	fields = ('class_field','name','portal','assignment_count')
	readonly_fields = ('class_field','assignment_count')

class AttendanceMonitorInline(admin.TabularInline):
	model = AttendanceMonitor
	fields = ('class_field','teacher')
	readonly_fields = ('class_field','teacher')

class ParentsInline(admin.TabularInline):
	model = Parent
	fields = ('p_id','first_name','last_name','phone')
	readonly_fields = ('p_id','first_name','last_name')

class ParentAddressInline(admin.TabularInline):
	model = ParentAddress
	fields = ('street','apt_no','city','region','country_code')

class ParentStudentInline(admin.TabularInline):
	model = StudentParent
	extra = 1

@admin.register(Classe)
class ClassAdmin(admin.ModelAdmin):
	list_display = ('class_id','description','level')
	list_filter = ('level','description')
	fields = ['attendance_monitor','description','level','start_date','end_date','class_url','completed']
	inlines = [SubjectInstancesInline,AttendanceRecordInline,EnrollmentInline]

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
	list_display = ('t_id','first_name','last_name','employed_at','is_monitor','education_level')
	list_filter = ('employed_at','education_level','is_monitor')
	fields = ['user','last_name','first_name','employed_at','dob','education_level','phone','is_monitor']
	inlines = [TeacherEnrollmentInline]

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
	list_display = ('assign_id','subject','entry_count','assignment_date')
	list_filter = ('subject_field__name',)
	fields = ['subject_field','assignment_date','description']
	inlines = [GradebookInline]


	def subject(self,obj):
		return obj.subject_field.name


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ('stud_id','last_name','first_name','student_level')
	list_filter = ('level',)
	fields = ['user','level','first_name','last_name','phone']
	#queryset = Student.objects.order_by('-stud_id')[:16]
	ordering = ('stud_id',)
	inlines = [StudAddressInline,ContactStudentInline,ParentStudentInline,StudentAttendanceInline,EnrollmentInline]

	def student_level(self,obj):
		if obj.level_id == 1:
			return '9A'
		elif obj.level_id == 2:
			return '9B'
		elif obj.level_id == 3:
			return '9C'
		elif obj.level_id == 4:
			return '9D'
		elif obj.level_id == 5:
			return '9E'
		else:
			return 'Not 9th Grader'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
	list_display = ('contact_id','last_name','first_name','email')
	list_filter = ('last_name',)
	fields = ['first_name','last_name','phone','email','notes']
	inlines = [ContactStudentInline]

@admin.register(EnrollmentRecord)
class EnrollmentAdmin(admin.ModelAdmin):
	list_display = ('enroll_id','fname','lname','class_name','student_level')
	list_filter = ('class_field__description',)
	fields = ['student','class_field','enrollment_start','enrollment_end','notes']

	def fname(self,obj):
		return str(obj.student.first_name)
	def lname(self,obj):
		return obj.student.last_name
	def student_level(self,obj):
		if obj.student.level_id == 4:
			return '9A'
		elif obj.student.level_id == 1:
			return 'some section'
		elif obj.student.level_id == 5:
			return '9B'
		elif obj.student.level_id == 6:
			return '9C'
		elif obj.student.level_id == 7:
			return '9D'
		elif obj.student.level_id == 8:
			return '9E'
		else:
			return 'unknown level'
	def class_name(self,obj):
		return obj.class_field.description

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
	list_display = ('class_field','session_date')
	list_filter = ('class_field',)
	fields = ['class_field','session_date','monitor'] #changed monitor_name to monitor here
	inlines = [StudentAttendanceInline]

#@admin.register(AttendanceMonitor)
class AttendanceMonitorAdmin(admin.ModelAdmin):
	list_display = ('monitor_id','class_name','teacher_name')
	list_filter = ('class_field__level__description',)
	fields = ['class_field','teacher']
	ordering = ('monitor_id',)
	inlines = [ClassesInline,AttendanceRecordInline]

	def class_name(self,obj):
		return obj.class_field.level.description
	def teacher_name(self,obj):
		return obj.teacher.first_name + ' ' +obj.teacher.last_name

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
	list_display = ('p_id','last_name','first_name')
	list_filter = ('last_name',)
	fields = ['user','first_name','last_name','phone']
	inlines = [ParentStudentInline]

@admin.register(Gradebook)
class GradebookAdmin(admin.ModelAdmin):
	actions = ['export_to_csv']
	list_display = ('student_name','subject','level','total','score','notes','stats')
	list_filter = ('assign__subject_field__name','assign__subject_field__class_description')
	fields = ['assign','student','submitted','graded_on','total','score']
	inlines = []

	def subject(self,obj):
		return obj.assign.subject_field.name
	def level(self,obj):
		return obj.assign.subject_field.class_description
	
	def export_to_csv(self,request,queryset):
		import csv
		from django.http import HttpResponse
		f=open('gradebook.csv','w')
		writer = csv.writer(f)
		writer.writerow(['student_name','subject','level','total','score','notes'])
		for each in queryset:
			writer.writerow([each.student_name,each.assign.subject_field.name,each.assign.subject_field.class_description,each.total,each.score,each.notes])
		f.close()
		f = open('gradebook.csv', 'r')
		response = HttpResponse(f, content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=stat-info.csv'

		return response

	export_to_csv.short_description = 'Download csv'

	# this calculated field cannot be used for filtering as is now but can be made. Just more code. Tired now!!
	def stats(self,obj):
		if obj.score <= 50:
			return 'Fail'
		elif(obj.score in range(50,60)):
			return 'F'
		elif(obj.score in range(60,70)):
			return 'D'
		elif(obj.score in range(70,80)):
			return 'C'
		elif(obj.score in range(80,90)):
			return 'B'
		elif(obj.score in range(90,101)):
			return 'A'
		else:
			return "seomthing is fucked up"

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
	list_display = ['session','student','attended','get_sessionDate',]
	def get_sessionDate(self, obj):
		return obj.session.session_date
	get_sessionDate.admin_order_field = 'session'
	list_filter = ('session__session_date',)
	fields = ['session','student','attended']
	inlines = []

@admin.register(ContactStudent)
class ContactStudentAdmin(admin.ModelAdmin):
	list_display = ('contact','student')
	list_filter = ('contact',)
	fields = ['contact', 'student']
	inlines = []

@admin.register(ContactAddress)
class ContactAddressAdmin(admin.ModelAdmin):
	list_display = ('contact','street','city','region','country_code')
	list_filter = ('city',)
	fields = ['contact','street','apt_no','city','region','country_code']
	inlines = []
@admin.register(ParentAddress)
class ParentAddressAdmin(admin.ModelAdmin):
	list_display = ('parent','street','city','region','country_code')
	list_filter = ('street',)
	fields = ['parent','street','city','region','country_code']
	inlines = []

@admin.register(SubjectInstance)
class SubjectInstance(admin.ModelAdmin):
	list_display = ('name','class_field')
	list_filter = ('class_field',)

@admin.register(TeacherEnrollment)
class TeacherEnrollment(admin.ModelAdmin):
	model = TeacherEnrollment
	list_display = ('teach_start','subject','fname','lname')
	list_filter = ('subj_field__name',)

	def subject(self,obj):
		return obj.subj_field.name
	def fname(sefl,obj):
		return obj.t.first_name
	def lname(self,obj):
		return obj.t.last_name
	def phone(self,obj):
		return obj.t.phone 

	class Meta:
		db_table = TeacherEnrollment
		verbose_name = 'Dept Teachers'