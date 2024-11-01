# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password

class User(AbstractUser):
    """
    Modelo base para usuarios del sistema con email como identificador
    y username y password encriptados.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Encrypt the username if it is not already encrypted
        if self.username and not self.username.startswith('pbkdf2_'):
            self.username = make_password(self.username)
        
       # Encrypt the password if it is not already encrypted
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email

class Student(models.Model):
    """
    Modelo específico para estudiantes
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)  # Student ID Number
    career = models.CharField(max_length=100) # Career that he/she studies
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"
    
    def get_average_grade(self):
        enrollments = self.enrollments.filter(is_completed=True)
        if not enrollments.exists():
            return 0.0
        return enrollments.aggregate(models.Avg('grade'))['grade__avg'] or 0.0

class Professor(models.Model):
    """
    Modelo específico para profesores
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile')
    professor_id = models.CharField(max_length=20, unique=True)  # Teacher ID number
    department = models.CharField(max_length=100) # Department to which it belongs
    title = models.CharField(max_length=100)  # Academic title
    specialization = models.CharField(max_length=200) # Area of ​​specialization
    
    def __str__(self):
        return f"Prof. {self.user.get_full_name()} - {self.department}"

class Subject(models.Model):
    """
    Modelo para materias
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Unique subject code
    description = models.TextField(null=True, blank=True)
    credits = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, related_name='subjects_taught')
    department = models.CharField(max_length=100, null=True, blank=True)
    semester_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['semester_number', 'name']
    
    def __str__(self):
        return f"{self.id} - {self.code} - {self.name}"

class Enrollment(models.Model):
    """
    Modelo para inscripciones
    """
    STATUS_CHOICES = [
        ('PE', 'Pending'),
        ('AC', 'Active'),
        ('CO', 'Completed'),
        ('CA', 'Cancelled'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='teaching_enrollments', default=1)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='PE')
    grade = models.FloatField(null=True, blank=True, 
                            validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    attendance = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    date_enrolled = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    semester_period = models.CharField(max_length=20, default="2024-1")
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'subject', 'semester_period']
        ordering = ['-date_enrolled']

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} ({self.semester_period})"

    @property
    def is_approved(self):
        return self.grade is not None and self.grade >= 3.0

    def save(self, *args, **kwargs):
        if self.grade is not None and not self.date_completed and self.is_completed:
            self.date_completed = timezone.now()
        super().save(*args, **kwargs)