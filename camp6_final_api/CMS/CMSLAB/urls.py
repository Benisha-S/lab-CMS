from django.urls import path
from .views import *

urlpatterns = [
    path('addemployee/',EmployeeCRUD.as_view()),
    path('employeelist/',EmployeeCRUD.as_view()),
    path('edit/<str:emp_id>',EmployeeCRUD.as_view()),
    path('disable/<str:emp_id>',EmployeeCRUD.as_view()),
    path('login',Login.as_view()),
    # departments
    # path('departments/',GetAllDepartments.as_view()),
    #qualification
    path('qualifications/',GetAllQualifications.as_view()),
    #specialization
    path('specialization/',GetAllSpecializations.as_view()),
    #gender
    path('gender/',GetAllGenders.as_view()),
    #role
    path('roles/',GetAllRoles.as_view()),
    #change password
    path('changepassword/',ChangePassword.as_view()),
    path('test_list', list_of_test),
    path('test_list/<int:passed_id>',testing_edit),
    path('live',live),
    path('details_list', list_of_values),
    path('list_of_values1', list_of_values1),
    path('details_list/<int:passed_id>', values_edit),
    path('search_test/<str:search_test>',search_test),
    path('diagnosis_list',diagnosis_list),
    path('diagnosis_info/<int:passed_id>',diagnosis_info),
    path('testPrescribed_list',testPrescribed_list),
    path('testPrescribed_info/<int:passed_id>',testPrescribed_info),
    path('isactivetruelist',testPrescribed_isactivetruelist),
    path('isactivefalselist',testPrescribed_isactivefalselist),
    path('isactivetrue/<int:passed_id>',testPrescribed_isactivetrue),
    path('isactivefalse/<int:passed_id>',testPrescribed_isactivefalse),
]