from django.db import models
from .managers import UserManager
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin,Group,Permission
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.contrib.auth.hashers import check_password as django_check_password

# Create your models here.

#admin
class Qualification(models.Model):
    qualification = models.CharField(max_length=250,null=False,blank=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.qualification

class Roles(models.Model):
    role_name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.role_name

#specialization
class Specialization(models.Model):
    specialization = models.CharField(max_length=100,blank=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.specialization

class Gender(models.Model):
    gender = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.gender
    
#employee info
class User(AbstractBaseUser,PermissionsMixin):
    emp_id = models.CharField(primary_key=True,editable=False,unique=True,max_length=10)
    first_name = models.CharField(max_length=30,null=False,blank=False)
    last_name = models.CharField(max_length=30,blank=False,null=True)
    address = models.CharField(max_length= 250,blank=False)
    dob = models.DateField(null=False,blank=False)
    contact_number = models.CharField(max_length=10,null=False,blank=True,default=0)
    gender = models.ForeignKey(Gender,on_delete=models.CASCADE,related_name="genders")
    qualification = models.ForeignKey(Qualification,on_delete=models.CASCADE,related_name="qualifications")
    date_of_joining = models.DateField(null=True,blank=False)
    email = models.EmailField(max_length=50,null=False,blank=False,unique=True)
    password = models.CharField(max_length=128,blank=False)
    role = models.ForeignKey(Roles,null=False,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    created_date = models.DateField(null=False,auto_now_add=True)
    groups = models.ManyToManyField(Group,related_name='custom_user_groups',blank=True)
    user_permissions = models.ManyToManyField(Permission,related_name='custom_user_permissions',blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['first_name','last_name','dob','password','is_staff']


    def check_password(self, raw_password):
        return super().check_password(raw_password)   

    

    def save(self,*args,**kwargs):
        # Only hash the password if it's being created or changed
        if self.pk is None:
            self.set_password(self.password)  # Hash password for new users

        if not self.emp_id:
            last_emp_id = User.objects.all().order_by('emp_id').last()
            if last_emp_id:
                last_id = int(last_emp_id.emp_id.split('Emp')[-1])
                new_id = last_id + 1
            else:
                new_id = 1000
            self.emp_id = f'Emp{new_id}'
        super().save(*args,**kwargs)

    def __str__(self):
        return f'User {self.emp_id} - {self.first_name}'


# doctors
class Doctors(models.Model):
    doc_id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User,on_delete=models.CASCADE,related_name="users")
    specialization = models.ForeignKey(Specialization,on_delete=models.CASCADE,related_name="specializations")
    fees = models.PositiveSmallIntegerField(null=False,blank=False,default=0)

    def __str__(self):
        return self.user_id.first_name
    

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

#hashing password
# @receiver(pre_save,sender=User)
# def hash_password(sender,instance,**kwargs):
#     if instance.pk is None or not instance.password.startswith('pbkdf2_sha256$'):
#         instance.password = make_password(instance.password)

class Counter(models.Model):
    name = models.CharField(max_length=50, unique=True)
    count = models.PositiveIntegerField(default=0)

def get_next_counter(name):
    counter, created = Counter.objects.get_or_create(name=name)
    counter.count += 1
    counter.save()
    return counter.count

def generate_opid():
    count = get_next_counter('patient_opid')
    return f"OP_{count:02d}"

def generate_token():
    count = get_next_counter('appointment_token')
    return f"Token {count}"

class patient_details(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    opid = models.CharField(max_length=10, default=generate_opid, unique=True, editable=False)
    name = models.CharField(max_length=50, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True)  # Date of birth
    age = models.PositiveIntegerField(null=True, blank=True)  # Age
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True)

    def _str_(self):
        return f"{self.name} ({self.opid})"

    def save(self, *args, **kwargs):
        # Calculate age if dob is provided
        if self.dob:
            self.age = timezone.now().year - self.dob.year
        super(patient_details, self).save(*args, **kwargs)


class BookAppointment(models.Model):
    TIME_SLOT_CHOICES = [
        ('09:00-09:30', '09:00-09:30 AM'),
        ('09:30-10:00', '09:30-10:00 AM'),
        ('10:00-10:30', '10:00-10:30 AM'),
        # Add more time slots as needed
    ]
    
    patient = models.ForeignKey(patient_details, related_name='appointments', on_delete=models.CASCADE, null=True)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, related_name="booked_appointments")
    doctor =  models.ForeignKey(Doctors,related_name='doctor',on_delete=models.CASCADE,null=True)
    appointment_date = models.DateField(null=True)
    time_slot = models.CharField(max_length=11, choices=TIME_SLOT_CHOICES, null=True)
    token = models.CharField(max_length=20, default=generate_token, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, null=True)

    def _str_(self):
        return f"Appointment for {self.patient.name} with Dr. {self.doctor} on {self.appointment_date} at {self.time_slot}"
    
    def save(self, *args, **kwargs):
        # Check if there are already 5 appointments for the given time slot
        existing_appointments = BookAppointment.objects.filter(
            appointment_date=self.appointment_date,
            time_slot=self.time_slot
        ).count()
        
        if (existing_appointments >= 5) and self.is_active:
            raise ValidationError(f"The time slot {self.time_slot} on {self.appointment_date} is fully booked.")
        
        super().save(*args, **kwargs)



class Diagnosis(models.Model):
    appointment = models.ForeignKey(BookAppointment, on_delete=models.CASCADE)
    medical_history = models.CharField(max_length=30, null=True)
    symptoms = models.CharField(max_length=100, null=True)
    diagnosis = models.CharField(max_length=100, null=True)
    doctor_note = models.CharField(max_length=100, null=True)
    next_visit = models.DateField(null=True, blank=True)

    def _str_(self):
        return f"Diagnosis for {self.appointment}"
    
class NewTest(models.Model):

    test_name = models.CharField(max_length=200, unique=True)
    low_value = models.IntegerField(blank=True, null=True)
    high_value = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=50)  # Assuming unit is a CharField for simplicity
    rate = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # BooleanField for isActive flag
    approved = models.BooleanField(default=False)  # BooleanField for approval status

    def _str_(self):
        return self.test_name
    
class TestPrescribed(models.Model):
    labtests = models.ForeignKey(Diagnosis, on_delete=models.CASCADE)
    date_of_prescribition = models.DateField(null=False)
    lab_tests = models.ManyToManyField(NewTest)
    is_active = models.BooleanField(default=True) 


    def _str_(self):
        return f"TestPrescribed for {self.labtests} on {self.date_of_prescribition}"

    
class LiveTest(models.Model):
    prescribed_test=models.ForeignKey(TestPrescribed, on_delete=models.CASCADE, related_name='details')
    tested_value = models.IntegerField()  
    comments = models.TextField(blank=True)  
    is_active = models.BooleanField(default=True) 
    
    def __str__(self):
        return f"{self.comments} - {self.tested_value}"


