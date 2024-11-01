from django.contrib import admin
from .models import User, Student, Professor, Subject, Enrollment

# Register your models here.
admin.site.register(User) 
admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Subject)
admin.site.register(Enrollment)
