from django.shortcuts import render_to_response, render, get_object_or_404,redirect # test
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import (Gradebook, StudAddress, Teacher, Assignment, AttendanceRecord, ClassLevel, Classe, ContactStudent, Contact, EnrollmentRecord, 
	StudentAttendance, Student, TeacherEnrollment, AttendanceMonitor, SubjectInstance, ContactAddress, Parent, ParentAddress,Fileuploads)
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min # dnt fucking forget this again. Ever!!
from .forms import StudentForm, StudentAddressForm, TeacherForm, AttendanceRecordForm, AssignmentForm, StudentAttendanceForm, GradebookForm, ContactForm, ContactAddressForm, ParentForm, ParentAddressForm,FileuploadsForm
from django.shortcuts import get_object_or_404, redirect

from django.contrib import messages
from .resources import StudentAttendanceDownload # dnt need this anymore.
import csv,io 
from django.core.files.storage import FileSystemStorage

@login_required()
def homepage(request):
	context = {}
	return render(request,'profiles/profile.html',context)
#test
@login_required
def class_list(request):
	#class_list1 = ['something','something2']
	attendances = list(Classe.objects.all())
	#class_list3 = list(class_list1)
	#context = { 'class_list2':class_list2, }
	return render(request,'profiles/student/student.html',{'class_list2':class_list2})

# students view of the attendance
@login_required
def student_attendance(self):
	attendances = StudentAttendance.objects.all()
	attendances = list(attendances)
	return render(request,'records/student/student.html',{'attendances':attendances})
# helper function
def _search_user(req,username):
	user = get_object_or_404(User,username=username)
	if username != req.user.username:
		user = None
	return user

# A detailed view of every subject. i.e 9A physics details - list of student and assignments...
@login_required
def teacher_course_page(request,username,pk):
	user = _search_user(request,username)
	course = None
	students = None
	assignments = None
	monitor = None
	if user != None:
		# The request is to get more info about a specific subject (The one the teacher teaches) so this is doing just by querying the db.
		course = SubjectInstance.objects.all().filter(inst_id=pk)
		# Just checking if the query returns nothing. Just incase.
		if len(course) != 0:
			course = course[0]
			# getting a list of all students.
			students = course.class_field.enrollmentrecord_set.all()
			# get all the assignments for the 'class'/ 'subject'
			assignments = course.assignment_set.all()
			files = Assignment.fileuploads_set
			#print(files)
			if user.teacher.is_monitor != 0:
				monitor = user.teacher.attendancemonitor_set.all()
				if len(monitor) != 0:
					monitor = monitor[0]
		else:
			course = None
	return render(request,'profiles/teacher/teacher_course.html',{'user':user,'course':course,'students':students,'assignments':assignments,'monitor':monitor,'files':files})

@login_required
def teacher_attendances(request,username):
	user = _search_user(request,username)
	attendances = None
	subjects = None
	if user != None:
		subjects = []
		for enrollment in user.teacher.teacherenrollment_set.all():
			subjects.append(enrollment.subj_field.inst_id)
		monitor = AttendanceMonitor.objects.all().filter(teacher = user.teacher.t_id)[0]
		attendances = monitor.attendancerecord_set.all()
	return render(request,'profiles/teacher/teacher_all_attendances.html',{'user':user,'attendances':attendances,'subjects':subjects})


# renders list of attendance for attendance monitor.
@login_required
def teacher_attendance(request,username,pk):
	user = _search_user(request,username)
	attendanceRecord = None
	if user != None:
		attendanceRecord = AttendanceRecord.objects.all().filter(session_id = pk)
		if len(attendanceRecord) > 0:
			attendanceRecord = attendanceRecord[0]
		else: 
			attendanceRecord = None

		#passing in class_id for
		#enrolled_records = []
		#student = EnrollmentRecord.objects.all().filter(class_field=class_id)
		#for each in student:
		#	enrolled_records.append(each)

		#enrolled = enrolled_records[0]

		#'students':enrolled

	return render(request,'profiles/teacher/attendance_list.html',{'user':user,'attendance':attendanceRecord})

# renders student detail for parent.
@login_required
def parent_student(request,username,pk):
	user = _search_user(request,username) #search_user returns the user or none if there is no
	student = None
	if user != None:
		student = user.parent.students.all().filter(stud_id=pk)
		if len(student) != 0:
			student = student[0]

	return render(request,'profiles/parent/student_detail.html',{'user':user,'student':student})

# this is invoke for 'add attendance' in teacher page
@login_required
def check_classes(request,username):
	user = _search_user(request,username)
	#set teacher to null.
	teacher = None
	#create a list for storing the classes the teacher is monitor for. It says 'course' so the name is a bit misleading here.
	courses = []
	# META is a dictionary containing all available HTTP headers. One of those is <HTTP_REFERER> which refers to the referring page. Good for security.
	path = request.META["HTTP_REFERER"]
	# Check if the user exists and is a teacher.
	if user != None and user.teacher:
		teacher = user.teacher
		# Get a list of all teachers in attendencemonitor table.
		monitors = teacher.attendancemonitor_set.all()
		# For each teacher get the corresponding classe they are monitor for. Class_field is a fk in attendancemonitor table to classe.
		for monitor in monitors:
			courses.append(monitor.class_field)
			# Note course is of type attendencemonitor The following courses gets passed to the template being rendered. We get the name of the class(9A, 9B) from inside the template and not here.
		courses = set(courses)
	return render(request,"profiles/teacher/check_course.html",{'user':user,'teacher':teacher,'courses':courses,'path':path})

# This will let you choose the day for which you are creating an attendence. I takes POST request from check_courses.html
@login_required
def add_attendance_record_form(request):
	if "course" in request.POST and request.POST["course"]:
		path = request.POST["path"]
		# we can assign the POST["Course"] because the value being submitted by the template invoking this view is course_id for each course. Eventhough the name is course.
		course_id = request.POST["course"]
		course = Classe.objects.all().filter(class_id=course_id)[0]
		attendance_monitor_id = course.attendance_monitor.monitor_id
		# Go get the date from add_attendance_form then go to saver view from there.Give the add_attendance_form all these as a hidden value. That will be a post request to the saver.
		return render(request,"profiles/teacher/add_attendance_form.html",{'monitor_id':attendance_monitor_id,'course_id':course_id,'path':path})
	return HttpResponse("The form you entered was invalid")

# for deleting the whole attendance record. i.e delete todays attendance record.
@login_required()
def delete_attendance(request,session_id):
	if request.method == 'POST':
		attendance = AttendanceRecord.objects.all().filter(session_id=session_id)
		attendance.delete()
	return redirect('Teacher_Homepage')

# for deleting one students' attendance record.
@login_required()
def delete_student_attendance_record(request,username,pk,attend_id):
	if request.method == 'POST':
		records = StudentAttendance.objects.all().filter(attend_id=attend_id)
		records.delete()
	return redirect('teacher_attendance_record',username=username, pk=pk)

# This will save all the fields needed for creating attendance to attendance table.
@login_required
def add_attendance_record_response(request):
	fields = ["monitor","course","session_date"]
	valid = True
	for field in fields:
		if field not in request.POST:
			valid = False
			break
	if valid:
		row = {}
		# this is creating the next pk for the insertions that follow.
		#last_attendance_id = AttendanceRecord.objects.all().aggregate(Max("session_id"))["session_id__max"]
		#last_attendance_id += 1
		#row["session_id"] = last_attendance_id

		# We need monitor Id to determine which monitor is adding attendence.
		monitor = AttendanceMonitor.objects.all().filter(monitor_id=request.POST["monitor"])[0]
		row["monitor"] = monitor
		#course seems to be a class (i.e 9A, 9B..)
		course = Classe.objects.all().filter(class_id=request.POST["course"])[0]
		row["class_field"] = course
		# The date we are creating calendar.
		row["session_date"] = request.POST["session_date"]
		#saving all the info to the table Attendence_record.
		attendance_record = AttendanceRecord(**row)
		attendance_record.save()

		path = request.POST["path"]
		return HttpResponseRedirect(path)
# Do the following if the entry isn't valid - i.e tried to enter attendance for the same date.
	return HttpResponse("The form you entered was invalid")

@login_required
def add_student_attendance_form(request,username,pk,session_id):
	user = _search_user(request,username)
	teacher = None
	students = []
	assignment = None
	path = request.META["HTTP_REFERER"]
	if user != None and user.teacher:
		teacher = user.teacher
		course = Classe.objects.all().filter(class_id=pk)
		if len(course) > 0:
			course = course[0]
		for enrollment in course.enrollmentrecord_set.all():
			students.append(enrollment.student)
		students = set(students)

		#new_students = []
		#my_students = EnrollmentRecord.objects.all().filter(class_field=pk)

		#for each in my_students:
			#new_students.append(each)

	return render(request,"profiles/teacher/add_student_attendance_form.html",{'user':user,'teacher':teacher,'students':students,'path':path,'session_id':session_id})

# detailed info about a given days attendance.
@login_required
def add_student_attendance_response(request):
	fields = ["session_id","student"]
	valid = True
	for field in fields:
		if field not in request.POST:
			valid = False
			break
	if valid:
		row = {}

		#last_student_attendance_id = StudentAttendance.objects.all().aggregate(Max("attend_id"))["attend_id__max"]
		#last_student_attendance_id += 1
		#row["attend_id"] = last_student_attendance_id


		session_id = request.POST["session_id"]
		attendance_record = AttendanceRecord.objects.all().filter(session_id=session_id)[0]
		row["session"] = attendance_record
		

		student_id = request.POST["student"]
		student_id = int(student_id)
		student = Student.objects.all().filter(stud_id=student_id)[0]
		row["student"] = student 

		row["attended"] = False
		if len(request.POST.getlist("attended")) > 0:
			row["attended"] = True

		if "notes" in request.POST and request.POST["notes"]:
			row["notes"] = request.POST["notes"]

		student_attendance = StudentAttendance(**row)
		student_attendance.save()

		path = request.POST["path"]
		return HttpResponseRedirect(path)
	return HttpResponse("The form you entered was not valid")

# update the date of a given days attendance.
@login_required
def update_attendance_record(request,username,pk):
	user = _search_user(request,username)
	instance = []
	if user != None:
		monitor = user.teacher.attendancemonitor_set.all()
		if len(monitor) > 0:
			monitor = monitor[0]
			instance = monitor.attendancerecord_set.all().filter(session_id=pk)

	if user == None or len(instance) == 0:
		return render(request,"500.html")

	instance = instance[0]
	form = AttendanceRecordForm(request.POST or None,instance=instance)
	if form.is_valid():
		
		form.save()
		if "view_name" in request.GET:
			view_name = request.GET.get("view_name")
			kwargs = request.GET.dict()
			del kwargs["view_name"]
			return redirect(view_name,**kwargs)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	return render(request,'profiles/teacher/attendance_record_update.html',{'form':form})

@login_required
def TeacherHomepage(request):
	return render(request,"profiles/teacher/teacher.html")

# edit already entered student attendance in the teacher page. Change the note and the status.
@login_required
def update_student_attendance(request,username,pk):
	user = _search_user(request,username)
	instance = []
	if user != None:
		instance = StudentAttendance.objects.all().filter(attend_id=pk)
		if len(instance) > 0:
			session_id = instance[0].session.session_id
			course = []
			for monitor in user.teacher.attendancemonitor_set.all():
				record = monitor.attendancerecord_set.all().filter(session_id=session_id)
				if len(record) > 0:
					course = record
	if user == None or len(instance) == 0 or len(course) == 0:
		return render(request,"500.html")
	instance = instance[0]
	form = StudentAttendanceForm(request.POST or None,instance=instance)
	if form.is_valid():
		form.save()
		if "view_name" in request.GET:
			view_name = request.GET.get("view_name")
			kwargs = request.GET.dict()
			del kwargs["view_name"]
			return redirect(view_name,**kwargs)
		return HttpResponseRedirect(request.META.get("HTTP_REFERER","/"))
	return render(request,"profiles/teacher/student_attendance_update.html",{'form':form})


# Download attendance of a specific session
@login_required()
def download_attendance(request,username,pk,session_id):
	user = _search_user(request,username)
	monitor = AttendanceMonitor.objects.filter(monitor_id=pk)
	students = StudentAttendance.objects.filter(student__level_id=pk,session_id=session_id)

	getStudents = []
	if user != None:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="attendance_record.csv"'
		writer = csv.writer(response)
		writer.writerow(['attended', 'Notes','StudentID','first_name','last_name'])
		for user in students:
			getStudents = Student.objects.all().filter(stud_id=user.student_id)
			for each in getStudents:
				writer.writerow([user.attended, user.notes,each.stud_id,each.first_name,each.last_name])
	return response

# Download attendance of a specific session
@login_required()
def download_all_attendance(request,username,pk):
	user = _search_user(request,username)
	monitor = AttendanceMonitor.objects.filter(monitor_id=pk)
	students = StudentAttendance.objects.filter(student__level_id=pk)

	getStudents = []
	if user != None:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="all_attendance_record.csv"'
		writer = csv.writer(response)
		writer.writerow(['attended', 'Notes','StudentID','first_name','last_name'])
		for user in students:
			getStudents = Student.objects.all().filter(stud_id=user.student_id)
			for each in getStudents:
				writer.writerow([user.attended, user.notes,each.stud_id,each.first_name,each.last_name])
	return response



# This receives request from teacher_assingments.html and renders the appopriate html.
@login_required
def add_assignment_form(request,username,pk):
	# intilize things to be rendered
	subject = None
	user = _search_user(request,username)
	path = request.META["HTTP_REFERER"]
	subjects = []
	# check if the user is not null and exists.
	if user != None and user.teacher:
		teacher = user.teacher
		# get all the subjects the teacher teaches through teacherenrollement table, where we can get access to subjectInstance through subj_field.
		for enrollment in teacher.teacherenrollment_set.all():
			subjects.append(enrollment.subj_field)
		if int(pk) > 0:
			# recall that subj_field is fk to Subjectinstance. Get the subjects the teacher teaches( the pk is 0 and nothing will be returned through this filter
			subjectInstance = teacher.teacherenrollment_set.all().filter(subj_field=int(pk))
			# if the teacher teaches more than one subject ??
			if len(subjectInstance) > 0:
				subject = subjectInstance[0].subj_field
			else:
				return render(request,"500.html",context={})
	return render(request,"profiles/teacher/add_assignment_form.html",{'user':user,'subjects':subjects,'path':path,'subject':subject})

# This is for saving the assignment to the 'assignment' table in my database. Every field in the table assingment will be assigned a value in this view.
@login_required
def add_assignment_response(request):
	# list of fields to check in the POST object.
	fields = ["subject","assignment_date","tasks"]
	valid = True
	# confirm the value of the fields is in POST request.
	for field in fields:
		if field not in request.POST:
			valid = False
			break
# if the value exist in the POST request, continue
	if valid:
		#myfile = request.FILES['myfile']
		row = {}
		# get the last assignment ID and increment it.
		last_assignment_id = Assignment.objects.all().aggregate(Max("assign_id"))["assign_id__max"]
		last_assignment_id = last_assignment_id + 1
		row["assign_id"] = last_assignment_id
		# to find for which subject I am adding the assignment, I need to check the fk which is in the POST object as 'subject' queried via subj.inst_id 
		subject = SubjectInstance.objects.all().filter(inst_id=request.POST["subject"])[0]
		row["subject_field"] = subject
		row["assignment_date"] = request.POST["assignment_date"]

		# get the description and save it.
		if "description" in request.POST and request.POST["description"]:
			row["description"] = request.POST["description"]
		
		if "tasks" in request.POST and request.POST["tasks"]:
			row["tasks"] = request.POST["tasks"]

		if request.method == 'POST':
			uploadedFile = request.FILES.get('document',False)

		fs = FileSystemStorage()
		name = fs.save(uploadedFile.name,uploadedFile)
		url = fs.url(name)
		row["pdf"] = name

		
	#	if "document" in request.POST and request.POST["document"]:
	#		row["document"] = request.FILES["document"]

		assignment = Assignment(**row)
		assignment.save()

		path = request.POST["path"]
		return HttpResponseRedirect(path)

	return HttpResponse("The form you entered was invalid")

# render elements for submitting the assignment entry.
@login_required
def teacher_assignment_entry(request,username,pk):
	user = _search_user(request,username)
	assignment = None
	if user != None:
		assignment = Assignment.objects.all().filter(assign_id = pk)
		files =Fileuploads.objects.all().filter(assignment=pk)
		if len(assignment) > 0:
			assignment = assignment[0]
		else:
			assignment = None
	return render(request,'profiles/teacher/teacher_assignment_entry.html',{'user':user,'assignment':assignment,'files':files})

# add grade for each student. This is for "Add Grade Entry"
@login_required
def add_gradebook_form(request,username,pk):
	user = _search_user(request,username)
	match = False
	students = []
	assignment = None
	path = request.META["HTTP_REFERER"]

	if user != None and user.teacher:
		for enrollment in user.teacher.teacherenrollment_set.all():
			assignment_set = enrollment.subj_field.assignment_set.all().filter(assign_id=pk)
			if len(assignment_set) > 0:
				match = True 
				assignment = assignment_set[0]
				break

	if not match:
		return render(request,"500.html",context={})

	for enrollment in assignment.subject_field.class_field.enrollmentrecord_set.all():
		students.append(enrollment.student)

	students = set(students)

	return render(request,"profiles/teacher/add_grade_form.html",{'user':user,'assign_id':pk,'students':students,'path':path})

# submit the grade entry by the teacher -[Add Grade Entry] button. elements are populated from the form using the view above.
@login_required
def add_gradebook_response(request):
	fields = ["assign_id","student","submitted","graded_on","total","score"]
	valid = True

	for field in fields:
		if field not in request.POST:
			valid = False
			break 

	if valid:
		row = {}
		#remove this to test not AI works. Might not need this.
		#last_grade_id = Gradebook.objects.all().aggregate(Max("grade_id"))["grade_id__max"]
		#last_grade_id += 1
		#row["grade_id"] = last_grade_id

		assignment = Assignment.objects.all().filter(assign_id=request.POST["assign_id"])[0]
		row["assign"] = assignment

		student = Student.objects.all().filter(stud_id=request.POST["student"])[0]
		row["student"] = student 

		row["submitted"] = request.POST["submitted"]
		row["graded_on"] = request.POST["graded_on"]
		row["total"]  = request.POST["total"]
		row["score"] = request.POST["score"]

		if "notes" in request.POST and request.POST["notes"]:
			row["notes"] = request.POST["notes"]

		gradebook = Gradebook(**row)
		gradebook.save()

		path = request.POST["path"]
		return HttpResponseRedirect(path)

	return HttpResponse("The form you submitted was invalid")

# @login_required()
# def delete_grade(request,grade_pk,assign_id,username):
# 	#user = _search_user(request,username)
# 	if request.method == 'POST':
# 		grades = Gradebook.objects.all().filter(grade_id=grade_pk)
# 		grades.delete()
# 	return redirect('teacher_assingments')

@login_required()
def delete_grade(request,username,grade_id,pk):
	print(grade_id)
	print(pk)
	print(username)
	#grades = Gradebook.objects.all().filter(grade_id=grade_id) #for test
	if request.method == 'POST':
		grades = Gradebook.objects.all().filter(grade_id=grade_id)
		grades.delete()
		# print(pk)
		# print(username)
	return redirect('teacher_assignment',username=username,pk=pk)


# class AuthorDelete(DeleteView):
#     model = Gradebook
#     success_url = reverse_lazy('teacher_assignments')


# edit-button at the top of each assignment detail used for updating uses this.
@login_required
def update_assignment_record(request,username,pk):
	user = _search_user(request,username)
	instance = []
	if user != None:
		instance = Assignment.objects.all().filter(assign_id=pk)
	if user == None or len(instance) == 0:
		return render(request,"500.html")
	instance = instance[0]
	form = AssignmentForm(request.POST or None,instance=instance)
	if form.is_valid():
		form.save()
		if "view_name" in request.GET:
			view_name = request.GET.get("view_name")
			kwargs = request.GET.dict()
			del kwargs["view_name"]
			return redirect(view_name,**kwargs)
		return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))
	return render(request,'profiles/teacher/assignment_update.html',{'form':form})


@login_required()
def parent_homepage(request):
	context = {}
	return render(request,'profiles/parent/parent.html',context)

# updating grades for each student's grade entry.

@login_required
def update_gradebook(request,username,pk):
	user = _search_user(request,username)
	instance = []
	match = False
	if user != None and user.teacher:
		instance = Gradebook.objects.all().filter(grade_id=pk)
		if len(instance) > 0:
			assign_id = instance[0].assign.assign_id
			subject_id = instance[0].assign.subject_field.inst_id 
			if len(user.teacher.teacherenrollment_set.all().filter(subj_field=subject_id)) > 0:
				match = True

	if not match:
		return render(request,"500.html",context={})

	instance = instance[0]
	form = GradebookForm(request.POST or None,instance=instance)
	if form.is_valid():
		form.save()
		if "view_name" in request.GET:
			view_name = request.GET.get("view_name")
			kwargs = request.GET.dict()
			del kwargs["view_name"]
			return redirect(view_name,**kwargs)
		return HttpResponseRedirect(request.META.get("HTTP_REFERER","/"))
	return render(request,"profiles/teacher/gradebook_update.html",{'form':form})


# For downloading the assignment
@login_required()
def download_assignment(request,username,pk):
	user = _search_user(request,username)
	gradebook = Gradebook.objects.all().filter(assign_id=pk)

	getStudents = []
	if user != None:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="csv_database_write.csv"'
		writer = csv.writer(response)
		writer.writerow(['first_name', 'last_name','Total','Score','Note'])
		for each in gradebook:
			writer.writerow([each.student.first_name, each.student.last_name,each.total,each.score,each.notes])
	return response

#download grades on student page
@login_required()
def student_download_assignment(request,username,pk):
	user = _search_user(request,username)
	gradebook = Gradebook.objects.filter(student=pk)

	getStudents = []
	if user != None:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="Student_Grade.csv"'
		writer = csv.writer(response)
		writer.writerow(['Subject', 'Description','Submitted Date','Grade Posted Date','Total','Your Score','Teacher Notes'])
		for grade in gradebook:
			writer.writerow([grade.assign.subject_field.name, grade.assign.description,grade.submitted,grade.graded_on,grade.total,grade.score,grade.notes])
	return response

#download attendance on student page
@login_required()
def student_download_attendance(request,username,pk):
	user = _search_user(request,username)
	attendance = StudentAttendance.objects.filter(student=pk)

	getStudents = []
	if user != None:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="Student_Grade.csv"'
		writer = csv.writer(response)
		writer.writerow(['Date', 'Attended','Monitor Notes'])
		for attend in attendance:
			writer.writerow([attend.session.session_date, attend.attended,attend.notes])
	return response

# Download grades from parent page
@login_required()
def parent_download_assignment(request,username,pk):
	user = _search_user(request,username)
	gradebook = Gradebook.objects.filter(student=pk)

	getStudents = []
	if user != None:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="Student_Grade.csv"'
		writer = csv.writer(response)
		writer.writerow(['Subject', 'Description','Submitted Date','Grade Posted Date','Total','Your Score','Teacher Notes'])
		for grade in gradebook:
			writer.writerow([grade.assign.subject_field.name, grade.assign.description,grade.submitted,grade.graded_on,grade.total,grade.score,grade.notes])
	return response

#download attendance from parent page.
@login_required()
def parent_download_attendance(request,username,pk):
	user = _search_user(request,username)
	attendance = StudentAttendance.objects.filter(student=pk)

	getStudents = []
	if user != None:
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="Student_Grade.csv"'
		writer = csv.writer(response)
		writer.writerow(['Date', 'Attended','Monitor Notes'])
		for attend in attendance:
			writer.writerow([attend.session.session_date, attend.attended,attend.notes])
	return response

@login_required()
def news_letter(request):
	context = {}
	return render(request,'profiles/teacher_news_letter.html',context)

@login_required()
def school_contacts(request):
	context = {}
	return render(request,'profiles/teacher_contact.html',context)
@login_required()
def parent_news_letter(request):
	context = {}
	return render(request,'profiles/parent_news_letter.html',context)

@login_required()
def parent_contacts(request):
	context = {}
	return render(request,'profiles/parent_contact.html',context)

@login_required()
def student_contacts(request):
	context = {}
	return render(request,'profiles/student_contact.html',context)

@login_required()
def student_news_letter(request):
	context = {}
	return render(request,'profiles/student_news_letter.html',context)

@login_required()
def student_homepage(request):
	context = {}
	return render(request,'profiles/student/student.html',context)

# return assignments to students for displaying uploaded assignments.
@login_required()
def student_tasks_page(request,username,pk):
	context = {}
	user = _search_user(request,username)
	course = None
	temp1 = []
	match = []

	if user != None:
		# The request is to get more info about a specific subject (The one the teacher teaches).
		records = EnrollmentRecord.objects.all().filter(student=pk)
		subject_in = SubjectInstance.objects.all()
		assign = Assignment.objects.all() # test and remvove this.
		for each in records:
			for each2 in subject_in:
				if each.class_field==each2.class_field:
					temp1.append(each2)

		assign = Assignment.objects.all().filter(subject_field__in=temp1)
		files = Fileuploads.objects.all().filter(student=pk)


	return render(request,'profiles/student/student_tasks_page.html',{'assignments':assign,'files':files})

@login_required()
def student_files_upload_list(request,pk):
	#user = _search_user(request,username)
	context = {}
	files = Fileuploads.objects.all().filter(student=pk)
	return render(request,'profiles/student/upload_list.html',{'files':files})

@login_required()
def upload_my_assignment(request,username,pk):
	user = _search_user(request,username)
	records = EnrollmentRecord.objects.all().filter(student=pk)
	student = Student.objects.all().filter(stud_id=pk)
	row = {}
	subjects = []
	temp1 = []

# Just for more info in the list page.
	records = EnrollmentRecord.objects.all().filter(student=pk)
	subject_in = SubjectInstance.objects.all()
	assign = Assignment.objects.all() # test and remvove this.
	for each in records:
		for each2 in subject_in:
			if each.class_field==each2.class_field:
				temp1.append(each2)

	assign = Assignment.objects.all().filter(subject_field__in=temp1)
	row = {}
	if request.method == 'POST':
		form = FileuploadsForm(request.POST or None, request.FILES)
		assign_save = Assignment.objects.all().filter(subject_field__in=temp1).filter(assign_id=request.POST["assignment"])[0]
		if "assignment" in request.POST and request.POST["assignment"]:
			row["assignment"] = assign_save

		#class_lev = ClassLevel.objects.all().filter(level_id=request.POST["class_level"])[0]
		student_save = Student.objects.all().filter(stud_id=str(pk))[0]
		# had to break some principles of request and get objects here but should work
		# for the time being. real trick trick here haha
		request.POST._mutable = True
		request.POST["student"] = str(pk)
		if form.is_valid():
			#form.save()
			row["student"] = student_save
			#row["classe"] = request.POST["classe"]
			row["pdf"] = request.FILES["pdf"]
			#row["submission_date"] = request.POST["submission_date"]
			#row["classe"] = request.POST["classe"]
			#row["class_level"] = class_lev

			upload = Fileuploads(**row)
			upload.save()			
			
			return redirect('upload_list_page',pk=pk)
	else:
		form = FileuploadsForm()
	return render(request,'profiles/student/upload_assignment.html',{'user':user,'form':form,'assignment':assign})

@login_required()
def delete_student_upload(request,pk,assignment_id,file_id):
	if request.method == 'POST':
		file_uploads = Fileuploads.objects.all().filter(student=pk).filter(assignment=assignment_id).filter(file_id=file_id)
		file_uploads.delete()	
	return redirect('upload_list_page',pk=pk)

@login_required()
def upload_grade(request,username,pk):
	template = 'profiles/teacher/upload_grade.html'
	prompt = { 'Order': 'Order of csv should be Assignment ID, student ID,submission Date, Graded Date, Total, Score,Notes. Put None in Note field if you have nothing to note.'}

	if request.method == 'GET':
		return render(request,template,prompt)
	csv_file = request.FILES['file']

	if not csv_file.name.endswith('.csv'):
		return HttpResponse("This is not a csv file. Please upload csv file!")

	data_set = csv_file.read().decode('UTF-8')
	io_string = io.StringIO(data_set)
	# with open(data_set,newline='') as f:
	# 	print(f)
	# print(io_string)
	for column in csv.reader(io_string,delimiter=",",quotechar="|"):
		print(column)
		i = 0
		student_instance = Student.objects.all().filter(stud_id=column[1])[i]
		i = i+1
		print(i)
		_,	created = Gradebook.objects.update_or_create(
			assign_id=column[0],
			student=student_instance,
			submitted=column[2],
			graded_on= column[3],
			total = column[4],
			score=column[5],
			notes=column[6])

	context = {}

	return redirect('teacher_assignment', username=username,pk=pk)