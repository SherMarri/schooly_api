from academics import models
from datetime import date


class ExamService:
    '''
    Service for managing operations related to examination.
    '''

    @staticmethod
    def create_exam(name, section, section_subjects):
        """
        Creates an exam and their corresponding assessments for students in the given section.
        
        Parameters:
            name (str): Name of the exam
            section (Model): Section for which to create the exam
            section_subjects ([dict]): An array of dict containing id and total marks of selected section subject
        
        Returns:
            Model: An instance of created exam
        """
        exam = models.Exam.objects.create(
            name=name, section_id=section['id'], consolidated=False, date=date.today()
        )

        assessments = []
        current_session = models.Session.objects.filter(is_active=True).first()

        for section_subject in section_subjects:
            assessment = models.Assessment(
                exam=exam, total_marks=section_subject['total_marks'],
                section_subject_id=section_subject['id'], date=date.today(),
                session=current_session
            )
            assessments.append(assessment)
        models.Assessment.objects.bulk_create(assessments)
        assessments = models.Assessment.objects.filter(exam=exam)
        student_ids = models.User.objects.filter(
            is_active=True, profile__student_info__section_id=section['id']
        ).values_list('id', flat=True)

        student_ids = [id for id in student_ids]
        student_assessments = []
        for assessment in assessments.all():
            for id in student_ids:
                student_assessment = models.StudentAssessment(
                    assessment=assessment, student_id=id
                )
                student_assessments.append(student_assessment)
        
        models.StudentAssessment.objects.bulk_create(student_assessments)
        return exam

    @staticmethod
    def create_consolidated_exam(name, section, exam_ids):
        """
        Creates a consolidated exam and their corresponding assessments for students in the given section.
        The final result of students for each section subject is compiled from provided exams with provided exam ids.
        
        Parameters:
            name (str): Name of the exam
            section (Model): Section for which to create the exam
            exam_ids ([int]): An array of integers containing ids of selected exams
        
        Returns:
            Model: An instance of created exam
        """
        exam = models.Exam(
            name=name, section=section, consolidated=True, date=date.today()
        ).save()

        """
        Fetch all assessments in provided exam ids and map each assessment against
        its section subject id
        """
        section_subjects = {}
        assessments = models.Assessment.objects.filter(exam_id__in=exam_ids)
        for assessment in assessments.all():
            if assessment.section_subject.id not in section_subjects:
                section_subjects[assessment.section_subject.id] = []
            section_subjects[assessment.section_subject.id].append(assessment)

        # Fetch students in provided section
        students = models.User.objects.filter(
            is_active=True, profile__student_info__section_id=section.id
        ).values('id').all()
        
        # Create consolidated assessments for each section subject
        for key, assessments in section_subjects.items():
            total_marks = 0
            for assessment in assessments:
                total_marks += assessment.total_marks
            
            assessment = models.Assessment(
                total_marks=total_marks, exam=exam, consolidated=True,
                section_subject_id=key
            ).save()

            student_assessments = []
            for id in students:
                student_assessment = models.StudentAssessment(
                    assessment=assessment, student_id=id
                )
                obtained_marks = models.StudentAssessment.objects.filter(
                    student_id=id, assessment_id__in=[
                        a.id for a in assessments
                    ]
                ).aggregate(obtained=Sum('obtained_marks')).obtained
                student_assessment.obtained_marks = obtained_marks
                student_assessments.append(student_assessment)
            models.StudentAssessment.objects.bulk_create(student_assessments)
        return exam
