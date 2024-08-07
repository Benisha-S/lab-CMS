from rest_framework.views import APIView
from .models import *
from .serializers import *
from django.http import JsonResponse,HttpResponse
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
# Create your views here.

#admin
#login
class Login(APIView):
    def post(self,request):
        employee = LoginSerializer(data=request.data)
        if employee.is_valid:
            email = employee.validated_data["email"]
            password = employee.validated_data["password"]
            auth_user = authenticate(request,email=email,password=password)
            if auth_user is not None:
                token = Token.objects.get(user=auth_user)
                #for getting the user as an object
                user_data = UserSerializer(auth_user).data
                print("hey hey")
                response ={
                    "status":status.HTTP_200_OK,
                    "message":"success",
                    "data":{
                        "Token":token.key,
                        "user":user_data
                    }
                }
                return Response (response,status = status.HTTP_200_OK)
            else:
                response = {
                     "status":status.HTTP_401_UNAUTHORIZED,
                    "message":"Invalid Username or password",
                }
                return Response(response,status=status.HTTP_401_UNAUTHORIZED)
        else:
            response = {
                "status":status.HTTP_400_BAD_REQUEST,
                "message":"Bad Request"
            }
            return Response(response,status=status.HTTP_400_BAD_REQUEST)

#employee management
class EmployeeCRUD(APIView):
    
    def get(self,request):
        employee_db = User.objects.filter(is_active=True)
        employee = UserSerializer(employee_db,many=True)
        return JsonResponse(employee.data,status = 200,safe=False)

    def post(self,request):
        role_id = request.data.get('role_id')
        employee_ser = UserSerializer(data=request.data)
        
        if employee_ser.is_valid():
            employee = employee_ser.save()
            print(role_id)
            print(type(role_id))
            if role_id == "3":
                print("1st here")
                doctor_data = {
                    'user_id': employee.emp_id,
                    'specialization': request.data.get('specialization_id'),
                    'fees': request.data.get('fees', 0)
                }
                print("2nd here")
                print(doctor_data)
                doctor = DoctorsSerializer(data=doctor_data)
                if doctor.is_valid():
                    doctor.save()
                    return JsonResponse(doctor.data, status=201, safe=False)
                else:
                    employee.delete()
                    return HttpResponse(doctor.errors, status=400)
            return JsonResponse(employee_ser.data, status=201, safe=False)
        return HttpResponse(employee_ser.errors, status=400)
            
    def put(self,request,emp_id):
        try:
            employee_db = User.objects.get(pk=emp_id)
        except User.DoesNotExist:
            return JsonResponse({"error":"Employee not Found"},status = 404)
        employee = UserSerializer(employee_db,data=request.data,partial=True)
        if employee.is_valid():
            emp=employee.save()
            if emp.role.id == "3":
                print(emp_id)
                try: 
                    doc = Doctors.objects.get(user_id=emp_id)
                except Doctors.DoesNotExist:
                    return JsonResponse({'error':"Doctor Not Found"},status=400)
                doc_data={
                    'specialization': request.data.get('specialization_id'),
                    'fees': request.data.get('fees', 0)
                }
                print("edit done")
                doc_ser=DoctorsSerializer(doc,data=doc_data,partial=True)
                if doc_ser.is_valid():
                    doc_ser.save()
                    return JsonResponse(doc_ser.data,status=200)
                return JsonResponse(doc_ser.errors,status=400)
            return JsonResponse(employee.data,status=200)
        return HttpResponse(employee.errors,status = 400)
    
    def delete(self,request,emp_id):
        employee_db = User.objects.get(pk= emp_id)
        employee_db.is_active = False
        employee_db.save()
        return JsonResponse({"message": "Employee deleted successfully"}, status= status.HTTP_204_NO_CONTENT)
    
    

#approvals
class AdminApproval(APIView):
    pass

    
#qualification
class GetAllQualifications(APIView):
    def get(self,request):
        qualification_db = Qualification.objects.all()
        qualifications = QualificationSerializer(qualification_db,many=True)
        return JsonResponse(qualifications.data,status=200,safe=False)
    
#specialization
class GetAllSpecializations(APIView):
    def get(self,request):
        specialization_db = Specialization.objects.all()
        specialization = SpecializationSerializer(specialization_db,many=True)
        return JsonResponse(specialization.data,status=200,safe=False)
    
#gender
class GetAllGenders(APIView):
    def get(self,request):
        gender_db = Gender.objects.all()
        gender = GenderSerializer(gender_db,many=True)
        return JsonResponse(gender.data,status=200,safe=False)
    
#role
class GetAllRoles(APIView):
    def get(self,request):
        try:
            roles_db = Roles.objects.all()
            roles = RolesSerializer(roles_db,many=True)
            return JsonResponse(roles.data,status=200,safe=False)
        except:
            return HttpResponse(roles.error_messages,status=400)

class ChangePassword(APIView):
    def patch(self,request,email):
        try:
            user_db = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"employee not found"},status=400)
        password = request.data.get('password')
        if password:
            user_db.password = make_password(password)
            user_db.save()
            return JsonResponse(user_db.data,status=200)
        return HttpResponse(user_db.errors,status=400)
@csrf_exempt
@api_view(['GET', 'POST'])
#@permission_classes((IsAuthenticated,))
def patient_list(request):
    if request.method == 'GET':
        patient_list = patient_details.objects.all()
        patient_list_serializer = PatientDetailSerializer(patient_list, many=True)
        return JsonResponse(patient_list_serializer.data, safe=False)

    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        patient_add_serializer = PatientDetailSerializer(data=request_data)
        if patient_add_serializer.is_valid():
            patient_add_serializer.save()
            return JsonResponse(patient_add_serializer.data, status=201)
        return JsonResponse(patient_add_serializer.errors, status=400)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def patient_info(request, passed_id):
    patient_info = patient_details.objects.get(id=passed_id)
    if request.method == 'GET':
        patient_info_serializer = PatientDetailSerializer(patient_info)
        return JsonResponse(patient_info_serializer.data, safe=False)

    elif request.method == "PUT":
        request_data = JSONParser().parse(request)
        patient_update_serializer = (PatientDetailSerializer(patient_info, data=request_data))
        if patient_update_serializer.is_valid():
            patient_update_serializer.save()
            return JsonResponse(patient_update_serializer.data, status=200)
        return JsonResponse(patient_update_serializer.errors, status=400)
    elif request.method == "DELETE":
        patient_info.delete()
        return HttpResponse(status=204)


def search_patient(request, search_Patient):
    patients = patient_details.objects.filter(
        Q(opid__icontains=search_Patient) | 
        Q(name__icontains=search_Patient) | 
        Q(mobile__icontains=search_Patient)
    )
    patient_serializer = PatientDetailSerializer(patients, many=True)
    return JsonResponse(patient_serializer.data, safe=False)


@csrf_exempt
@api_view(['GET', 'POST'])
#@permission_classes((IsAuthenticated,))
def appointment_list(request):
    if request.method == 'GET':
        appoint_list = BookAppointment.objects.all()
        appoint_list_serializer = BookAppointmentSerializer(appoint_list, many=True)
        return JsonResponse(appoint_list_serializer.data, safe=False)

    elif request.method == 'POST':
        appoint_add_serializer = BookAppointmentSerializer(data=request.data)
        if appoint_add_serializer.is_valid():
            appoint_add_serializer.save()
            return JsonResponse(appoint_add_serializer.data, status=201)
        return JsonResponse(appoint_add_serializer.errors, status=400)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def appointment_info(request, passed_id):
    appoint_info = BookAppointment.objects.get(id=passed_id)
    if request.method == 'GET':
        appoint_serializer = BookAppointmentSerializer(appoint_info)
        return JsonResponse(appoint_serializer.data, safe=False)

    elif request.method == "PUT":
        request_data = JSONParser().parse(request)
        appoint_update_serializer = (BookAppointmentSerializer(appoint_info, data=request_data))
        if appoint_update_serializer.is_valid():
            appoint_update_serializer.save()
            return JsonResponse(appoint_update_serializer.data, status=200)
        return JsonResponse(appoint_update_serializer.errors, status=400)
    elif request.method == "DELETE":
        appoint_info.delete()
        return HttpResponse(status=204)


def search_appointment(request, search_appoint):
    appoint = BookAppointment.objects.filter(doctor__icontains=search_appoint)
    appoint_serializer = BookAppointmentSerializer(appoint, many=True)
    return JsonResponse(appoint_serializer.data, safe=False)
    
#doctor

@csrf_exempt
@api_view(['GET','POST'])
def testPrescribed_list(request):
    if request.method == 'GET':
        test_prescribed_list = TestPrescribed.objects.all()
        test_prescribed_serializer = TestPrescribedSerializer(test_prescribed_list, many=True)
        return JsonResponse(test_prescribed_serializer.data, safe=False)
    
    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        test_prescribed_add_serializer = TestPrescribedSerializer(data=request_data)
        if test_prescribed_add_serializer.is_valid():
            test_prescribed_add_serializer.save()
            return JsonResponse(test_prescribed_add_serializer.data, status=201)
        return JsonResponse(test_prescribed_add_serializer.errors, status=400)
@api_view(['GET','POST'])
def testPrescribed_isactivetruelist(request):
    if request.method == 'GET':
        test_prescribed_list = TestPrescribed.objects.filter(is_active=True)
        test_prescribed_serializer = TestPrescribedSerializer(test_prescribed_list, many=True)
        return JsonResponse(test_prescribed_serializer.data, safe=False)
    
    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        test_prescribed_add_serializer = TestPrescribedSerializer(data=request_data)
        if test_prescribed_add_serializer.is_valid():
            test_prescribed_add_serializer.save()
            return JsonResponse(test_prescribed_add_serializer.data, status=201)
        return JsonResponse(test_prescribed_add_serializer.errors, status=400)
    
@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def testPrescribed_isactivetrue(request, passed_id):
    try:
        test_prescribed_instance = TestPrescribed.objects.get(is_active=True, id=passed_id)
    except TestPrescribed.DoesNotExist:
        return JsonResponse({'error': 'Test Prescribed not found'}, status=404)

    if request.method == 'GET':
        test_prescribed_serializer = TestPrescribedSerializer(test_prescribed_instance)
        return JsonResponse(test_prescribed_serializer.data)

    elif request.method == 'DELETE':
        test_prescribed_instance.is_active = False
        test_prescribed_instance.save()
        return JsonResponse({'message': 'Test Prescribed deactivated successfully'}, status=204)
@api_view(['GET','POST'])
def testPrescribed_isactivefalselist(request):
    if request.method == 'GET':
        test_prescribed_list = TestPrescribed.objects.filter(is_active=False)
        test_prescribed_serializer = TestPrescribedSerializer(test_prescribed_list, many=True)
        return JsonResponse(test_prescribed_serializer.data, safe=False)
    
    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        test_prescribed_add_serializer = TestPrescribedSerializer(data=request_data)
        if test_prescribed_add_serializer.is_valid():
            test_prescribed_add_serializer.save()
            return JsonResponse(test_prescribed_add_serializer.data, status=201)
        return JsonResponse(test_prescribed_add_serializer.errors, status=400)  

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def testPrescribed_isactivefalse(request, passed_id):
    try:
        test_prescribed_instance = TestPrescribed.objects.get(is_active=False, id=passed_id)
    except TestPrescribed.DoesNotExist:
        return JsonResponse({'error': 'Test Prescribed not found'}, status=404)

    if request.method == 'GET':
        test_prescribed_serializer = TestPrescribedSerializer(test_prescribed_instance)
        return JsonResponse(test_prescribed_serializer.data)

    elif request.method == 'DELETE':
        test_prescribed_instance.is_active = True
        test_prescribed_instance.save()
        return JsonResponse({'message': 'Test Prescribed deactivated successfully'}, status=204)
@csrf_exempt
@api_view(['GET','POST'])
def testPrescribed_list2(request):
    if request.method == 'GET':
        test_prescribed_list = User.objects.all()
        test_prescribed_serializer = UserSerializer(test_prescribed_list, many=True)
        return JsonResponse(test_prescribed_serializer.data, safe=False)
    
    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        test_prescribed_add_serializer = UserSerializer(data=request_data)
        if test_prescribed_add_serializer.is_valid():
            test_prescribed_add_serializer.save()
            return JsonResponse(test_prescribed_add_serializer.data, status=201)
        return JsonResponse(test_prescribed_add_serializer.errors, status=400)


@csrf_exempt
@api_view(['GET','POST'])
def testPrescribed_list1(request):
    if request.method == 'GET':
        test_prescribed_list = Doctors.objects.all()
        test_prescribed_serializer = DoctorsSerializer(test_prescribed_list, many=True)
        return JsonResponse(test_prescribed_serializer.data, safe=False)
    
    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        test_prescribed_add_serializer = DoctorsSerializer(data=request_data)
        if test_prescribed_add_serializer.is_valid():
            test_prescribed_add_serializer.save()
            return JsonResponse(test_prescribed_add_serializer.data, status=201)
        return JsonResponse(test_prescribed_add_serializer.errors, status=400)

#lab_technician


@csrf_exempt
@api_view(['GET','POST'])
def diagnosis_list(request):
    if request.method == 'GET':
        diagnosis_list = Diagnosis.objects.all()
        diagnosis_list_serializer = DiagnosisSerializer(diagnosis_list, many=True)
        return JsonResponse(diagnosis_list_serializer.data, safe=False)

    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        diagnosis_add_serializer = DiagnosisSerializer(data=request_data)
        if diagnosis_add_serializer.is_valid():
            diagnosis_add_serializer.save()
            return JsonResponse(diagnosis_add_serializer.data, status=201)
        return JsonResponse(diagnosis_add_serializer.errors, status=400)


@csrf_exempt
@api_view(['GET','PUT','DELETE'])
def diagnosis_info(request, passed_id):
    try:
        diagnosis_info = Diagnosis.objects.get(id=passed_id)
    except Diagnosis.DoesNotExist:
        return JsonResponse({'error': 'Diagnosis not found'}, status=404)

    if request.method == 'GET':
        diagnosis_serializer = DiagnosisSerializer(diagnosis_info)
        return JsonResponse(diagnosis_serializer.data, safe=False)
    
    elif request.method == 'PUT':
        request_data = JSONParser().parse(request)
        diagnosis_update_serializer = DiagnosisSerializer(diagnosis_info, data=request_data)
        if diagnosis_update_serializer.is_valid():
            diagnosis_update_serializer.save()
            return JsonResponse(diagnosis_update_serializer.data, status=200)
        return JsonResponse(diagnosis_update_serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        diagnosis_info.delete()
        return HttpResponse(status=204)

@csrf_exempt
@api_view(['GET','POST'])
def testPrescribed_list(request):
    if request.method == 'GET':
        testPrescribed_list = TestPrescribed.objects.all()
        test_prescribed_serializer = TestPrescribedSerializer(testPrescribed_list, many=True)
        return JsonResponse(test_prescribed_serializer.data, safe=False)
    
    elif request.method == 'POST':
        request_data = JSONParser().parse(request)
        test_prescribed_add_serializer = TestPrescribedSerializer(data=request_data)
        if test_prescribed_add_serializer.is_valid():
            test_prescribed_add_serializer.save()
            return JsonResponse(test_prescribed_add_serializer.data, status=201)
        return JsonResponse(test_prescribed_add_serializer.errors, status=400)

@csrf_exempt
@api_view(['GET','PUT','DELETE'])
def testPrescribed_info(request, passed_id):
    try:
        test_info = TestPrescribed.objects.get(id=passed_id)
    except TestPrescribed.DoesNotExist:
        return JsonResponse({'error': 'TestPrescribed not found'}, status=404)

    if request.method == 'GET':
        test_serializer = TestPrescribedSerializer(test_info)
        return JsonResponse(test_serializer.data, safe=False)
    
    elif request.method == 'PUT':
        request_data = JSONParser().parse(request)
        test_update_serializer = TestPrescribedSerializer(test_info, data=request_data)
        if test_update_serializer.is_valid():
            test_update_serializer.save()
            return JsonResponse(test_update_serializer.data, status=200)
        return JsonResponse(test_update_serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        test_info.delete()
        return HttpResponse(status=204)
    


@csrf_exempt
@api_view(['GET', 'POST'])
def list_of_test(request):
    if request.method == "GET":
        testing = NewTest.objects.all()
        testing_serialize = NewTest_Serializer(testing, many=True)
        return JsonResponse(testing_serialize.data, safe=False)

    elif request.method == 'POST':
        try:
            request_data = JSONParser().parse(request)
            testing_deserialize = NewTest_Serializer(data=request_data)

            if testing_deserialize.is_valid():
                testing_deserialize.save()
                return JsonResponse(testing_deserialize.data, status=201)
            return JsonResponse(testing_deserialize.errors, status=400)

        except JSONParser.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    # Handle unsupported HTTP methods
    return JsonResponse({'error': 'Method not allowed'}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from .models import NewTest
from .serializers import *

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def testing_edit(request, passed_id):
    try:
        test_details = NewTest.objects.get(id=passed_id)
    except NewTest.DoesNotExist:
        return JsonResponse({'error': 'Test with specified ID not found'}, status=404)

    if request.method == 'GET':
        test_list_serializer = NewTest_Serializer(test_details)
        return JsonResponse(test_list_serializer.data, safe=False)

    elif request.method == "PUT":
        request_data = JSONParser().parse(request)
        test_update_serializer = NewTest_Serializer(test_details, data=request_data)
        if test_update_serializer.is_valid():
            test_update_serializer.save()
            return JsonResponse(test_update_serializer.data, status=200)
        return JsonResponse(test_update_serializer.errors, status=400)

    elif request.method == 'DELETE':
        test_details.delete()
        return JsonResponse({'message': 'Test deleted successfully'}, status=204)

    # Handle unsupported HTTP methods
    return JsonResponse({'error': 'Method not allowed'}, status=405)

    
def search_test(request, search_test):
    test = NewTest.objects.filter( Q(test_name__icontains=search_test) )
    test_serializer = NewTest_Serializer(test, many=True)
    return JsonResponse(test_serializer.data, safe=False)



    

@api_view(['GET','POST'])
def list_of_values(request):
    if request.method=="GET":
        value_details=LiveTest.objects.all()
        print(value_details)
        value_serialize=LiveTest_serializers(value_details,many=True)
        print(value_serialize.data)
        return JsonResponse(value_serialize.data,safe=False)
    elif request.method=='POST':
        value_deserialize=LiveTest_serializers(data=request.data)
        if value_deserialize.is_valid():
            value_deserialize.save()
            return JsonResponse(value_deserialize.data, status=201)
        return JsonResponse(value_deserialize.errors, status=400)
@api_view(['GET'])
def list_of_values1(request):
    if request.method=="GET":
        value_details=LiveTest.objects.filter(is_active=False)
        print(value_details)
        value_serialize=LiveTest_serializers(value_details,many=True)
        print(value_serialize.data)
        return JsonResponse(value_serialize.data, safe=False)
    elif request.method=='POST':
        value_deserialize=LiveTest_serializers(data=request.data)
        if value_deserialize.is_valid():
            value_deserialize.save()
            return JsonResponse(value_deserialize.data, status=201)
        return JsonResponse(value_deserialize.errors, status=400)
    
@csrf_exempt
@api_view(['GET','PUT','DELETE'])
def values_edit(request,passed_id):
    value_details=LiveTest.objects.get(id=passed_id)
    if request.method == 'GET':
        test_list_serializer = LiveTest_serializers(value_details)
        return JsonResponse(test_list_serializer.data, safe=False)
    if request.method=="PUT":
        request_data=JSONParser().parse(request)
        value_update_serializer=(
            LiveTest_serializers(value_details,data=request_data))
        if value_update_serializer.is_valid():
            value_update_serializer.save()
            return JsonResponse(value_update_serializer.data,status=200)
        return JsonResponse(value_update_serializer.errors,status=400)
    if request.method == 'DELETE':
        # value_details.delete()
        value_details.is_active = False
        value_details.save()
        return JsonResponse(status=204)
@csrf_exempt
@api_view(['GET','POST'])
def live(request):
    if request.method=="GET":
        value_details=LiveTest.objects.all()
        print(value_details)
        value_serialize=LiveTest_serializers(value_details,many=True)
        print(value_serialize.data)
        return JsonResponse(value_serialize.data,safe=False)
    elif request.method=='POST':
        value_deserialize=LiveTest_serializers(data=request.data)
        if value_deserialize.is_valid():
            value_deserialize.save()
            return JsonResponse(value_deserialize.data, status=201)
        return JsonResponse(value_deserialize.errors, status=400)
    
from rest_framework import generics
from .models import LiveTest
from .serializers import LiveTest_serializers

class LiveTestCreateView(generics.CreateAPIView):
    queryset = LiveTest.objects.all()
    serializer_class = LiveTest_serializers

