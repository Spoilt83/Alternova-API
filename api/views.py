# views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg
from .models import Subject, Enrollment, Student, Professor
from .serializers import SubjectSerializer, EnrollmentSerializer, StudentSerializer, ProfessorSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone

class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        return Enrollment.objects.filter(student=student)

    # 1. A student signs up for a list of subjects
    @action(detail=False, methods=['post'])
    def enroll_subjects(self, request):
        student = get_object_or_404(Student, user=request.user)
        subject_ids = request.data.get('subject_ids', [])
        
        if not subject_ids:
            return Response(
                {"error": "No subject IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollments = []
        errors = []

        for subject_id in subject_ids:
            try:
                subject = Subject.objects.get(id=subject_id)
                
                # Check prerequisites
                for prereq in subject.prerequisites.all():
                    if not Enrollment.objects.filter(
                        student=student,
                        subject=prereq,
                        is_completed=True,
                        grade__gte=3.0
                    ).exists():
                        errors.append(f"Prerequisite {prereq.name} not met for {subject.name}")
                        continue

                # Check if you are already enrolled in the current period
                if Enrollment.objects.filter(
                    student=student,
                    subject=subject,
                    semester_period="2024-1"
                ).exists():
                    errors.append(f"Already enrolled in {subject.name}")
                    continue

                # Create registration
                enrollment = Enrollment.objects.create(
                    student=student,
                    subject=subject,
                    professor=subject.professor,
                    semester_period="2024-1",
                    status='AC'
                )
                enrollments.append(enrollment)

            except Subject.DoesNotExist:
                errors.append(f"Subject with ID {subject_id} does not exist")

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

   # 2. A student can get the list of subjects he is enrolled in
    @action(detail=False, methods=['get'])
    def my_subjects(self, request):
        student = get_object_or_404(Student, user=request.user)
        enrollments = Enrollment.objects.filter(
            student=student,
            status='AC'
        )
        serializer = self.get_serializer(enrollments, many=True)
        return Response(serializer.data)

    # 4. A student can get the list of his passed subjects and his average
    @action(detail=False, methods=['get'])
    def approved_subjects(self, request):
        student = get_object_or_404(Student, user=request.user)
        approved_enrollments = Enrollment.objects.filter(
            student=student,
            grade__gte=3.0,
            is_completed=True
        )
        
        average = student.get_average_grade()
        serializer = self.get_serializer(approved_enrollments, many=True)
        
        return Response({
            'subjects': serializer.data,
            'average': round(average, 2)
        })

    # 5. Check the subjects a student has failed
    @action(detail=False, methods=['get'])
    def failed_subjects(self, request):
        student = get_object_or_404(Student, user=request.user)
        failed_enrollments = Enrollment.objects.filter(
            student=student,
            grade__lt=3.0,
            is_completed=True
        )
        serializer = self.get_serializer(failed_enrollments, many=True)
        return Response(serializer.data)

class ProfessorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubjectSerializer

    # 6 and 7. A teacher can have and obtain the list of assigned subjects
    def get_queryset(self):
        professor = get_object_or_404(Professor, user=self.request.user)
        return Subject.objects.filter(professor=professor)

   # 8. A teacher can see the list of students for each of his subjects
    @action(detail=True, methods=['get'])
    def student_list(self, request, pk=None):
        professor = get_object_or_404(Professor, user=request.user)
        
        # Get the subject using pk
        subject = get_object_or_404(Subject, pk=pk)
        
        if subject.professor != professor:
            return Response(
                {"error": "You are not authorized to view this subject's students"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Filter student enrollments in the subject    
        enrollments = Enrollment.objects.filter(
            subject=subject,
            status='AC'
        ).select_related('student')
        
        # Serialize the data
        data = [{
            'student_id': enrollment.student.student_id,
            'name': enrollment.student.user.get_full_name(),
            'grade': enrollment.grade,
            'status': enrollment.status
        } for enrollment in enrollments]
        
        return Response(data)

   # 9. A teacher finishes the subject (grades each student)
    @action(detail=True, methods=['post'])
    def grade_students(self, request, pk=None):
        professor = get_object_or_404(Professor, user=request.user)
        subject = self.get_object()
        
        if subject.professor != professor:
            return Response(
                {"error": "You are not authorized to grade this subject"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        grades_data = request.data.get('grades', [])
        
        updated_enrollments = []
        errors = []
        
        for grade_info in grades_data:
            try:
                enrollment = Enrollment.objects.get(
                    subject=subject,
                    student__student_id=grade_info['student_id'],
                    status='AC'
                )
                
                enrollment.grade = grade_info['grade']
                enrollment.is_completed = True
                enrollment.status = 'CO'
                enrollment.date_completed = timezone.now()
                enrollment.save()
                
                updated_enrollments.append(enrollment)
                
            except Enrollment.DoesNotExist:
                errors.append(f"Student {grade_info['student_id']} not found in this subject")
            except KeyError:
                errors.append("Invalid grade data format")
        
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = EnrollmentSerializer(updated_enrollments, many=True)
        return Response(serializer.data)

    # 10. A teacher can get students' grades in their subjects
    @action(detail=True, methods=['get'])
    def student_grades(self, request, pk=None):
        professor = get_object_or_404(Professor, user=request.user)
        subject = self.get_object()
        
        if subject.professor != professor:
            return Response(
                {"error": "You are not authorized to view this subject's grades"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        enrollments = Enrollment.objects.filter(
            subject=subject
        ).select_related('student')
        
        data = [{
            'student_id': enrollment.student.student_id,
            'name': enrollment.student.user.get_full_name(),
            'grade': enrollment.grade,
            'status': enrollment.status,
            'date_completed': enrollment.date_completed
        } for enrollment in enrollments]
        
        return Response(data)