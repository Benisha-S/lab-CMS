from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

# class DepartmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model= Department
#         fields = '__all__'

class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = '__all__'

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'

class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'




class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'

    #qualification
    qualification = QualificationSerializer(read_only = True)
    qualification_id = serializers.PrimaryKeyRelatedField(queryset=Qualification.objects.all())
    #Gender
    gender = GenderSerializer(read_only=True)
    gender_id = serializers.PrimaryKeyRelatedField(queryset=Gender.objects.all())
    #role
    role = RolesSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Roles.objects.all())

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        qualification = validated_data.pop('qualification_id')
        gender = validated_data.pop('gender_id')
        role = validated_data.pop('role_id')

        user = User.objects.create(
            **validated_data
        )

        print("2nd here")
        user.qualification = qualification
        user.gender = gender
        user.role = role

        user.save()

        return user
    
    def update(self,instance,validated_data):
        qualification_data = validated_data.pop('qualification_id')
        gender_data = validated_data.pop('gender_id')
        role_data = validated_data.pop('role_id')
        #for hasing the password
        # password = validated_data.pop('password')
        # if password:
        #     hashed_password = make_password(password)
        #     instance.password = hashed_password

        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.address = validated_data.get('address',instance.address)
        instance.dob = validated_data.get('dob',instance.dob)
        instance.date_of_joining = validated_data.get('date_of_joining',instance.date_of_joining)
        instance.contact_number = validated_data.get('contact_number',instance.contact_number)

        #updatng the related fields
        if isinstance(qualification_data, dict):
            qualification, created = Qualification.objects.get_or_create(**qualification_data)
            instance.qualification = qualification
        if isinstance(gender_data, dict):
            gender, created = Gender.objects.get_or_create(**gender_data)
            instance.gender = gender
        if isinstance(role_data, dict):
            role, created = Roles.objects.get_or_create(**role_data)
            instance.role = role
        
        instance.save()
        return instance
class DoctorsSerializer(serializers.ModelSerializer):
    user_id=UserSerializer(read_only=True)
    class Meta:
        model = Doctors
        fields = '__all__'
    
#login
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password= serializers.CharField(max_length=128,write_only=True)
    role = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['email','password','role']

class PatientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = patient_details
        fields = '__all__'

class BookAppointmentSerializer(serializers.ModelSerializer):
    patient = PatientDetailSerializer(read_only=True)
    specialization = SpecializationSerializer(read_only=True)
    doctor = DoctorsSerializer(read_only=True)

    class Meta:
        model = BookAppointment
        fields = '__all__'
class NewTest_serializer(serializers.ModelSerializer):
    class Meta:
        model = NewTest
        fields = '__all__'

class DiagnosisSerializer(serializers.ModelSerializer):
    appointment = serializers.PrimaryKeyRelatedField(queryset=BookAppointment.objects.all())
    patient = serializers.SerializerMethodField()

    class Meta:
        model = Diagnosis
        fields = '__all__'

    def create(self, validated_data):
        # Directly use the appointment instance
        diagnosis = Diagnosis.objects.create(**validated_data)
        return diagnosis

    def update(self, instance, validated_data):
        appointment_data = validated_data.pop('appointment', None)
        if appointment_data:
            instance.appointment = appointment_data
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_patient(self, obj):
        return PatientDetailSerializer(obj.appointment.patient).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['appointment'] = BookAppointmentSerializer(instance.appointment).data
        representation['patient'] = representation['appointment']['patient']  # Directly assign patient from appointment
        return representation



class TestPrescribedSerializer(serializers.ModelSerializer):
    labtests = serializers.PrimaryKeyRelatedField(queryset=Diagnosis.objects.all())
    patient = serializers.SerializerMethodField()
    lab_tests = serializers.PrimaryKeyRelatedField(queryset=NewTest.objects.all(), many=True, write_only=True)
    lab_tests_details = NewTest_serializer(many=True, read_only=True, source='lab_tests')

    class Meta:
        model = TestPrescribed
        fields = '__all__'

    def create(self, validated_data):
        lab_tests_data = validated_data.pop('lab_tests')
        test_prescribed = TestPrescribed.objects.create(**validated_data)
        test_prescribed.lab_tests.set(lab_tests_data)
        return test_prescribed

    def update(self, instance, validated_data):
        lab_tests_data = validated_data.pop('lab_tests', None)
        if lab_tests_data:
            instance.lab_tests.set(lab_tests_data)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def get_patient(self, obj):
        # Access the patient through the appointment in the Diagnosis model
        return PatientDetailSerializer(obj.labtests.appointment.patient).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['labtests'] = DiagnosisSerializer(instance.labtests).data
        representation['patient'] = representation['labtests']['appointment']['patient']
        return representation
    

class NewTest_Serializer(serializers.ModelSerializer):
    class Meta:
        model = NewTest
        fields = '__all__'


class LiveTest_serializers(serializers.ModelSerializer):
    test = TestPrescribedSerializer(read_only=True)
    

    class Meta:
        model = LiveTest
        fields = ['id', 'prescribed_test','test' ,'tested_value', 'comments', 'is_active']


    def create(self, validated_data):
        prescribed_test = validated_data.pop('prescribed_test',None)
        # Create the LiveTest instance
        live_test = LiveTest.objects.create(**validated_data,prescribed_test=prescribed_test)
        return live_test

    def update(self, instance, validated_data):
        instance.tested_value = validated_data.get('tested_value', instance.tested_value)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['test'] = TestPrescribedSerializer(instance.prescribed_test).data
        return rep


