from django.urls import path
from . import views


#the following three for header
from django.contrib import admin
from django.conf import settings
admin.site.site_header = settings.ADMIN_SITE_HEADER
from django.conf.urls import url

urlpatterns = [
path('',views.homepage, name='homepage')
]

urlpatterns += [
url(r'profiles/$',views.TeacherHomepage,name='Teacher_Homepage'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/course/(?P<pk>\d+)/$',views.teacher_course_page,name='teacher_course_page'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/attendance/(?P<pk>\d+)/$',views.teacher_attendance,name='teacher_attendance_record'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/student/(?P<pk>\d+)/$',views.parent_student,name='parent_student'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/attendance/add/$',views.check_classes,name='teacher_attendance_add'),
]

urlpatterns += [
url(r'^add_attendance_confirm_class/$',views.add_attendance_record_form,name='add_attendance_confirm_class'),
url(r'^add_attendance_record/$',views.add_attendance_record_response,name='add_attendance_record'),
#url(r'^add_attendance_record/$',views.add_attendance_record_response,name='add_attendance_record'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/course/(?P<pk>\d+)/session/(?P<session_id>\d+)/student-attendance/add/$',views.add_student_attendance_form,name='teacher_add_student_attendance'),
]

# form action for adding each student attendance.
urlpatterns += [
url(r'^add_student_attendance/$',views.add_student_attendance_response,name='add_student_attendance'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/attendance/(?P<pk>\d+)/update/$',views.update_attendance_record,name='teacher_attendance_update'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/attendances-teacher/$',views.teacher_attendances,name='teacher_all_attendances'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/student-attendance/(?P<pk>\d+)/update/$',views.update_student_attendance,name='teacher_update_student_attendance'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/download_attendance/(?P<pk>\d+)/session_date/(?P<session_id>\d+)/',views.download_attendance,name='download_attendance'),
]


urlpatterns += [
url(r'^user/(?P<username>\w+)/download_all_attendance/(?P<pk>\d+)/',views.download_all_attendance,name='download_all_attendance'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/download_assignment/(?P<pk>\d+)/$',views.download_assignment,name='download_assignment'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/student_download_assignment/(?P<pk>\d+)/$',views.student_download_assignment,name='student_download_assignment'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/student_download_attendance/(?P<pk>\d+)/',views.student_download_attendance,name='student_download_attendance'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/parent_download_assignment/(?P<pk>\d+)/',views.parent_download_assignment,name='parent_download_assignment'),
]

urlpatterns += [
url(r'^user/(?P<username>\w+)/parent_download_attendance/(?P<pk>\d+)/',views.parent_download_attendance,name='parent_download_attendance'),
]


urlpatterns += [
	url(r'^user/(?P<username>\w+)/assignment/(?P<pk>\d+)/add/$',views.add_assignment_form,name='teacher_add_assignment'),
]

urlpatterns += [
	url(r'^add_assignment/$',views.add_assignment_response,name='add_assignment'),
]

urlpatterns += [
	url(r'^delete/gradeentry/(?P<username>\w+)/grade/(?P<grade_id>\d+)/assign/(?P<pk>\d+)/$', views.delete_grade,name='delete_grade'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/assignment/(?P<pk>\d+)/done/$',views.teacher_assignment_entry,name='teacher_assignment'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/assignment/(?P<pk>\d+)/gradebook/add/$',views.add_gradebook_form,name='teacher_add_grade'),
]

urlpatterns += [
	url(r'^add_grade_entry/$',views.add_gradebook_response,name='add_grade_entry'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/assignment/(?P<pk>\d+)/update/$',views.update_assignment_record,name='teacher_update_assignment'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/gradebook/(?P<pk>\d+)/update/$',views.update_gradebook,name='teacher_update_grade')
]

urlpatterns += [
url(r'more/newsletter/$',views.news_letter,name='teacher_news_letter'),
]


urlpatterns += [
url(r'parent/newsletter/$', views.parent_news_letter,name='parent_news_letter')
]

urlpatterns += [
	url(r'home/parent/$', views.parent_homepage,name='parent_homepage'),
]

urlpatterns += [
url(r'parent/contact/$',views.parent_contacts,name='parent_contacts'),
]

urlpatterns += [
url(r'schoolcontact/contact/$',views.school_contacts,name='school_contacts'),
]

urlpatterns += [
url(r'student/newsletter/$', views.student_news_letter,name='student_news_letter')
]

urlpatterns += [
url(r'student/contact/$',views.student_contacts,name='student_contacts'),
]

urlpatterns += [
	url(r'home/student/$', views.student_homepage,name='student_homepage'),
]

urlpatterns += [
	url(r'^user/(?P<username>\w+)/tasks/(?P<pk>\d+)/page/$', views.student_tasks_page,name='student_tasks'),
]

urlpatterns += [
	url(r'^submission/list/(?P<pk>\d+)/page/$', views.student_files_upload_list,name='upload_list_page'),
]

urlpatterns += [
	url(r'^submit/(?P<username>\w+)/assignment/(?P<pk>\d+)/page/$', views.upload_my_assignment,name='upload_my_assignment'),
]


urlpatterns += [
	url(r'^student/delete/(?P<pk>\d+)/done/(?P<assignment_id>\d+)/(?P<file_id>\d+)/$', views.delete_student_upload,name='delete_student_upload'),
]


urlpatterns += [
	url(r'^teacher/delete/(?P<session_id>\d+)/done/$', views.delete_attendance,name='delete_attendance'),
]

urlpatterns += [
	url(r'^delete/user/(?P<username>\w+)/record/(?P<pk>\d+)/attendance/(?P<attend_id>\d+)/return/$', views.delete_student_attendance_record,name='delete_student_attendance_record'),
]


urlpatterns += [
	url(r'^upload-grade/(?P<username>\w+)/id/(?P<pk>\d+)/$', views.upload_grade,name='upload_grade'),
]



