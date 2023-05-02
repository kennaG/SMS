# Model for school management system.

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import re

class Assignment(models.Model):
    assign_id = models.AutoField(primary_key=True)
    subject_field = models.ForeignKey('SubjectInstance', models.CASCADE,default = None,db_column='inst_id')  # Field renamed because it was a Python reserved word.
    description = models.CharField(max_length=512, blank=True, null=True)
    assignment_date = models.DateField(default=None)
    tasks = models.CharField(max_length=512,blank=True,null=True)
    pdf = models.FileField(upload_to='assignments/',null=True)

    class Meta:
        managed = True
        db_table = 'assignments'

    @property
    def entry_count(self):
        return len(self.gradebook_set.all())

    # @property
    # def files(self):
    #     return Fileuploads_set.all()

    def __str__(self):
        return "Class %d: %s" % (self.assign_id,self.subject_field.inst_id)

class AttendanceMonitor(models.Model):
    monitor_id = models.AutoField(primary_key=True)
    class_field = models.ForeignKey('Classe',models.CASCADE,default=None,db_column='class_id')
    teacher = models.ForeignKey('Teacher',models.CASCADE,default=None,db_column='t_id')

    class Meta:
        managed = True
        db_table = 'attendance_monitor'

    @property
    def attendance_snippet(self):
        return self.attendancerecord_set.all()[:10]

    def __str__(self):
        return "Monitor for Course %d: %s, %s" % (self.class_field.class_id,self.teacher.last_name,self.teacher.first_name)



class AttendanceRecord(models.Model):
    session_id = models.AutoField(primary_key=True)
    class_field = models.ForeignKey('Classe', models.CASCADE,default = None, db_column='class_id')  # Field renamed because it was a Python reserved word.
    monitor = models.ForeignKey('AttendanceMonitor', models.CASCADE,default = None,db_column='monitor_id')
    session_date = models.DateField()

    class Meta:
        managed = True
        db_table = 'attendance_records'

    @property
    def class_name(self):
        return self.class_field.class_name

    @property
    def entry_count(self):
        return len(self.studentattendance_set.all())

    @property
    def monitor_name(self):
        return "%s %s" % (self.monitor.teacher.first_name,self.monitor.teacher.last_name)

    def __str__(self):
        return "Attendance Record %d" % (self.session_id)

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ClassLevel(models.Model):
    level_id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    monitor_teacher = models.ForeignKey('AttendanceMonitor',models.DO_NOTHING,default=None,db_column='monitor_teacher')
    
    class Meta:
        ordering = ["level_id"]
        managed = True
        db_table = 'class_levels'

    @property
    def get_level_code(self):
        desc = str(self.description)
        if len(desc) == 0 or desc == "None":
            return "No Code"
        return desc.replace("grade","")

    @property
    def get_class_count(self):
        return self.classe_set.count()

    def __str__(self):
        return "%s" % (self.description)

class Classe(models.Model):
    class_id = models.AutoField(primary_key=True)
    attendance_monitor = models.ForeignKey(AttendanceMonitor,models.CASCADE,default=None,blank=True,null=True)
    description = models.CharField(max_length=512, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    class_url = models.CharField(unique=False, max_length=80, blank=True, null=True)
    level = models.ForeignKey(ClassLevel,models.PROTECT,default=None)
    completed = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'classes'

    def get_absolute_url(self):
        return reverse('classe-detail',args=[str(self.class_id)])

    def __str__(self):
        return "Class %d : %s" % (self.class_id,self.class_name)

    @property
    def complete_code(self):
        if self.completed == 1:
            return "Completed"
        return "In Progress"

    @property
    def teacher_enrollment(self):
        teacher_set = []
        for subject in self.subjectinstance_set.all():
            teachers = list(subject.teacherenrollment_set.all())
            teacher_set += teachers
        return teacher_set

    @property
    def enroll_count(self):
        count = 0
        for subject in self.subjectinstance_set.all():
            count += len(subject.assignment_set.all())
        return count

    @property
    def monitor_name(self):
        return "%s %s" % (self.attendance_monitor.teacher.first_name,self.attendance_monitor.teacher.last_name)

    def get_absolute_url(self):
        return reverse('classe-detail',args=[str(self.class_id)])

    def __str__(self):
        return "Class %d : %s" % (self.class_id,self.description)





class ContactAddress(models.Model):
    address_key = models.AutoField(primary_key=True)
    contact = models.ForeignKey('Contact',models.CASCADE,default = None)
    street = models.CharField(max_length=100)
    apt_no = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=60)
    region = models.CharField(max_length=60)
    country_code = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'contact_addresses'

    def __str__(self):
        apartment = ""
        if self.apt_no != None:
            apartment = self.apt_no
        return "%s %s %s %s %s" % (apartment,self.street,self.city,self.region,self.country_code)

class ContactStudent(models.Model):
    #pair_id = models.AutoField(primary_key=True)
    contact = models.ForeignKey('Contact', models.CASCADE,default = None)
    student = models.ForeignKey('Student', models.CASCADE,default = None)

    class Meta:
        managed = True
        db_table = 'contact_students'
        #unique_together = (('contact', 'student'),)

    def __str__(self):
        return ""

class Contact(models.Model):
    contact_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    phone = models.CharField(max_length=25)
    email = models.CharField(max_length=128, blank=True, null=True)
    notes = models.CharField(max_length=512)

    class Meta:
        managed = True
        db_table = 'contacts'

    def __str__(self):
        return "%s %s" % (self.first_name,self.last_name)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EducationLevel(models.Model):
    education_key = models.AutoField(primary_key=True)
    EDUCATION_CHOICES = (
        ('BS','Bachelors of Science'),
        ('MS','Masters of Science'),
        ('BA','Bachelors of Arts'),
        ('MA','Masters of Arts'),
        ('MEng','Masters of Engineering'),
        ('PhD','University Doctorate'),
        ('PsyD','Psychology Doctorate'),
        ('MD','Medical Doctorate'),
        ('JD','Juris Doctorate'),
    )
    education = models.CharField(max_length = 5, choices = EDUCATION_CHOICES,Blank=True,Null=True)

    class Meta:
        managed = True
        db_table = 'education_levels'
        
    def __str__(self):
        return "%s" % (self.education)


class EnrollmentRecord(models.Model):
    enroll_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Student', models.CASCADE,default = None)
    class_field = models.ForeignKey(Classe, models.CASCADE,default = None,db_column='class_id')  # Field renamed because it was a Python reserved word.
    enrollment_start = models.DateField()
    enrollment_end = models.DateField()
    notes = models.TextField(blank=True, null=True)

    @property
    def class_name(self):
        return self.class_field.class_name

    @property
    def first_name(self):
        return self.student.first_name

    @property
    def last_name(self):
        return self.student.last_name

    @property
    def email(self):
        return self.student.user.email

    class Meta:
        managed = True
        db_table = 'enrollment_records'
        verbose_name = 'ተማሪዎች'

    def __str__(self):
        return "Enrollment Number %d" % (self.enroll_id)


class Gradebook(models.Model):
    grade_id = models.AutoField(primary_key=True)
    assign = models.ForeignKey(Assignment, models.CASCADE,default = None)
    student = models.ForeignKey('Student', models.CASCADE,default = None)
    submitted = models.DateField(null=True)
    graded_on = models.DateField(null=True)
    total = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    notes = models.CharField(max_length=512, blank=True, null=True)
    #description = models.CharField(max_length=255,blank=True,null=True)

    class meta:
        managed = True

    @property
    def grade(self):
        total = 100 * (float(self.score) / float(self.total))
        if total >= 90.0:
            return "A"
        if total >= 80.0:
            return "B"
        if total >= 70.0:
            return "C"
        if total >= 60.0:
            return "D"
        return "F"


    @property
    def student_name(self):
        return ("%s %s") % (self.student.first_name,self.student.last_name)

    @property
    def format_score(self):
        correction = 100 * (float(self.score) / float(self.total))
        return "%.2f" % correction

    class Meta:
        managed = True
        db_table = 'gradebook'

    def __str__(self):
        return "Assignment %d Score: %.2f" % (self.assign.assign_id,100.0 * float(self.score/self.total))

class Parent(models.Model):
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING,default=None)
    p_id = models.AutoField(primary_key=True)
    students = models.ManyToManyField('Student',null=False,through="StudentParent")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=25)

    class Meta:
        managed = True
        db_table = 'parent'

    def __str__(self):
        return "Parent %d: %s %s" % (self.p_id,self.first_name,self.last_name)

class ParentAddress(models.Model):
    address_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('Parent',models.CASCADE,default=True)
    street = models.CharField(max_length=100)
    apt_no = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=60)
    region = models.CharField(max_length=60)
    country_code = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'parent_addresses'

    def __str__(self):
        apartment = ""
        if self.apt_no != None:
            apartment = self.apt_no
        return "%s %s %s %s %s" % (apartment,self.street,self.city,self.region,self.country_code)
    

class SubjectInstance(models.Model):
    inst_id = models.AutoField(primary_key=True)
    class_field = models.ForeignKey(Classe,models.CASCADE,default=True)
    name = models.CharField(max_length=60)
    portal = models.CharField(unique=False, max_length=80, blank=True, null=True)
    class_description = models.CharField(unique=False,max_length=2,blank=True,null=True)
    
    class Meta:
        managed = True
        db_table = 'subject_instance'

    @property
    def assignment_count(self):
        return len(self.assignment_set.all())
    @property
    def subject_list(self):#test
        return self._subject_list
    

    def __str__(self):
        return "Subject for Course %d: %s" % (self.class_field.class_id,self.name)

class StudAddress(models.Model):
    address_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('Student', models.CASCADE,default = None)
    street = models.CharField(max_length=100)
    apt_no = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=60)
    region = models.CharField(max_length=60)
    country_code = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'stud_addresses'


    def __str__(self):
        apartment = ""
        if self.apt_no != None:
            apartment = self.apt_no
        return "%s %s %s %s %s" % (apartment,self.street,self.city,self.region,self.country_code)



class StudentAttendance(models.Model):
    attend_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(AttendanceRecord, models.CASCADE,default = None)
    student = models.ForeignKey('Student', models.CASCADE,default = None)
    attended = models.BooleanField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'student_attendances'

    @property
    def attendance_date(self):
        return self.session.session_date
    @property
    def attendace(self):
        return self.attendancerecord_set.all
    
    # def attendancerecord(self):
    #     return self.attendancerecord_set.all

    def __str__(self):
        return "Record %d for Student %d" % (self.attend_id,self.student.stud_id)

class StudentParent(models.Model):
    record_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey('Parent',models.CASCADE,default=None)
    student = models.ForeignKey('Student',models.CASCADE,default=None)
    notes = models.TextField(blank=True,null=True)

    class Meta:
        managed = True
        db_table = 'parent_students'

    def __str__(self):
        return "Relation %d: Student %s with Parent %s" % (self.record_id,str(self.student),str(self.parent))

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING,default=None)
    stud_id = models.AutoField(primary_key=True)
    dob = models.DateField()
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    level = models.ForeignKey(ClassLevel, models.PROTECT,default = None)
    phone = models.CharField(max_length=25, blank=True, null=True)
    parents = models.ManyToManyField(Parent,through='StudentParent')
    contacts = models.ManyToManyField(Contact,through = "ContactStudent")
    gender = models.CharField(max_length=5,blank=True,null=True)
    class Meta:
        ordering  = ["last_name"]
        managed = True
        db_table = 'students'
        permissions = (('can_add_any_person','Can add students,classes, and teachers.'),)

    @property
    def attendance_snippet(self):
        return self.studentattendance_set.all()[:7]
    
    @property
    def format_phone(self):
        phone_str = str(self.phone)
        formatted = format(int(phone_str[:-1]),",").replace(",","-") + phone_str[-1]
        return formatted

    @property
    def address(self):
        results = StudAddress.objects.all().filter(student_id=self.stud_id)
        if len(results) == 0:
            return "No address on file"
        address = results[0]
        return str(address)

    @property
    def absences(self):
        return StudentAttendance.objects.all().filter(student=self.stud_id,attended=0)

    @property
    def subject_set(self):
        subjects = []
        for course in self.enrollmentrecord_set.all():
            for subject in course.class_field.subjectinstance_set.all():
                subjects.append(subject.name)

        subjects = set(subjects)
        return subjects

    @property
    def assignment_count(self):
        return len(self.gradebook_set.all())

    @property
    def assignment_snippet(self):
        return self.gradebook_set.all()
    

    @property
    def class_snippet(self):
        return self.enrollmentrecord_set.all()[:5]

    @property
    def grade_snippet(self):
        return self.gradebook_set.all()[:5]

    @property
    def contact_snippet(self):
        return self.contacts.all()[:2]

    def get_absolute_url(self):
        return reverse('student-detail',args=[str(self.stud_id)])

    def __str__(self):
        return "%d : %s %s" % (self.stud_id,self.first_name,self.last_name)


class TeacherEnrollment(models.Model):
    tenroll_id = models.AutoField(primary_key=True)
    t = models.ForeignKey('Teacher', models.CASCADE,default = None,)
    subj_field = models.ForeignKey(SubjectInstance, models.CASCADE, default = None,db_column='inst_id')  # Field renamed because it was a Python reserved word.
    teach_start = models.DateField()
    class_start = models.DateField()
    class_end = models.DateField()
    grade_due = models.DateField()
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["teach_start"]
        managed = True
        db_table = 'teacher_enrollments'
        verbose_name = 'Dept Teacher'

    @property
    def class_name(self):
        return self.subj_field.class_field.class_name

    @property
    def teacher(self):
        return "%s %s" % (self.t.first_name,self.t.last_name)

    def __str__(self):
        return "Teacher Enrollment Code: %d" % (self.tenroll_id)


class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING,default=None)
    is_monitor = models.BooleanField(default=False)
    t_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    dob = models.DateField()
    employed_at = models.DateField()
    education_level = models.ForeignKey(EducationLevel,models.DO_NOTHING,default=None, db_column='education_key')
    #email = models.CharField(unique=True, max_length=80)
    #passphrase = models.CharField(max_length=80)
    phone = models.CharField(max_length=25)
    site = models.CharField(unique=False,max_length=255,blank=True,null=True)


    class Meta:
        ordering = ["employed_at"]
        managed = True
        db_table = 'teachers'
        permissions = (('can_add_any_person','Can add students,classes, and teachers.'), ('Can add gradebook', 'Can add gradebook'),('Can Add Student Attendance','Can Add Student Attendance'),('Can add attendance record','Can add attendance record'),)

    @property
    def format_phone(self):
        phone_str = str(self.phone)
        formatted = format(int(phone_str[:-1]),",").replace(",","-") + phone_str[-1]
        return formatted

    @property
    def class_snippet(self):
        return self.teacherenrollment_set.all()[:5]

    @property
    def all_assignments(self):
        assignments = []
        for enrollment in self.teacherenrollment_set.all():
            assignment_set = list(enrollment.subj_field.assignment_set.all())
            assignments += assignment_set
        return assignments

    @property
    def attendance_snippet(self):
        snippet = None
        if self.is_monitor == 1:
            monitor = self.attendancemonitor_set.all()[0]
            snippet = monitor.attendancerecord_set.order_by('-session_date')
            snippet = snippet[:7]
        return snippet

    
    @property
    def assignment_snippet(self):
        return self.all_assignments()[:5]

    def get_absolute_url(self):
        return reverse('teacher-detail',args=[str(self.t_id)])

    def __str__(self):
        return "Teacher %d: %s %s" % (self.t_id,self.first_name,self.last_name)


class Fileuploads(models.Model):
    file_id = models.AutoField(primary_key=True)
    pdf = models.FileField(upload_to='submissions/',null=True)
    student = models.ForeignKey('Student',on_delete=None,default='uknown',db_column='student',null=True)
    assignment = models.ForeignKey('Assignment',on_delete=None,default='uknown',db_column='assignment',null=True)
    submission_date = models.DateField(auto_now=True,null=True)
    #teacher = models.ForeignKey('Teacher',on_delete=None,default=None,db_column='t_id')

    class Meta:
        managed = True
        db_table ='student_uploads'