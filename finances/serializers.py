from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts import models as accounts_models
from finances import models
from structure.models import Grade
import json

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExpenseCategory
        fields = ('id', 'name', 'description')


class ExpenseItemSerializer(serializers.ModelSerializer):
    category = ExpenseCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.ExpenseCategory.objects.all(),
        source='category'
    )

    class Meta:
        model = models.ExpenseItem
        fields = ('id', 'title', 'category_id', 'category', 'description',
                  'amount', 'date')


class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IncomeCategory
        fields = ('id', 'name', 'description')


class IncomeItemSerializer(serializers.ModelSerializer):
    category = IncomeCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=models.IncomeCategory.objects.all(),
        source='category'
    )

    class Meta:
        model = models.IncomeItem
        fields = ('id', 'title', 'category_id', 'category', 'description',
                  'amount', 'date')


class FeeStructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.FeeStructure
        fields = ('id', 'name', 'description', 'break_down', 'total')


class CreateChallanSerializer(serializers.Serializer):

    description = serializers.CharField(max_length=128)
    structure_id = serializers.IntegerField()
    target_type = serializers.CharField(max_length=20)
    due_date = serializers.DateField()
    target_value = serializers.JSONField()

    def save(self, **kwargs):
        data = self.validated_data
        
        if data['target_type'] == 'individuals':  # Fetch ids from target_value
            ids = data['target_value']
        else:
            target_value = data['target_value']
            if target_value['grade_id'] == -1:  # All grades
                ids = [a[0] for a in accounts_models.StudentInfo.objects.filter(
                    is_active=True).values_list('profile__user_id')]
            else:
                if target_value['section_id'] == -1:  # All sections of a grade
                    ids = [a[0] for a in accounts_models.StudentInfo.objects.filter(
                        is_active=True,
                        section__grade_id=target_value['grade_id']
                        ).values_list('profile__user_id')]
                else:
                    ids = [a[0] for a in accounts_models.StudentInfo.objects.filter(
                        is_active=True,
                        section_id=target_value['section_id']
                        ).values_list('profile__user_id')]

        challans = []
        structure = models.FeeStructure.objects.get(id=data['structure_id'])
        for id in ids:
            challan = models.FeeChallan()
            challan.student_id = id
            challan.break_down = structure.break_down
            challan.total = structure.total
            challan.due_date = data['due_date']
            challan.description = data['description']
            
            challans.append(challan)
        
        models.FeeChallan.objects.bulk_create(challans)


    def validate_structure_id(self, value):
        try:
            models.FeeStructure.objects.get(id=value)
        except:
            raise serializers.ValidationError("Invalid structure id")
        else:
            return value

    def validate_target_type(self, value):
        if value in ['individuals', 'group']:
            return value
        else:
            raise serializers.ValidationError('Invalid target type')

    def validate_target_value(self, value):
        target_type = self.initial_data['target_type']
        if target_type == 'individuals':
            try:
                ids = value
                count = accounts_models.User.objects.filter(id__in=ids).count()
                if len(ids) == count:
                    return ids
                raise serializers.ValidationError('Invalid student ids provided')
            except:
                raise serializers.ValidationError('Invalid student ids provided')
        else:  # Group
            grade_id = value.get('grade_id', None)
            if grade_id is None:
                raise serializers.ValidationError('Grade ID missing')
            if grade_id == -1:  # If not all grades
                return {
                    'grade_id': -1
                }

            grade = Grade.objects.filter(id=grade_id).prefetch_related('sections').first()
            if grade is None:
                raise serializers.ValidationError('Grade does not exist')

            section_id = value.get('section_id', None)
            if section_id is None:
                raise serializers.ValidationError('Section ID missing')
            elif section_id == -1:
                return {
                    'grade_id': grade_id,
                    'section_id': -1
                }
            else:
                section = grade.sections.filter(id=section_id).first()
                if section is None:
                    raise serializers.ValidationError('Section does not exist')
                return {
                    'grade_id': grade_id,
                    'section_id': section_id
                }


class FeeChallanSerializer(serializers.ModelSerializer):
    break_down = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = models.FeeChallan
        fields = ('id', 'student', 'break_down', 'total', 'paid', 'discount',
            'due_date', 'paid_at', 'paid_by', 'description', 'received_by')
        
    def get_break_down(self, obj):
        return json.loads(obj.break_down)

    def get_student(self, obj):
        return {
            'id': obj.student.id,
            'fullname': obj.student.profile.info.fullname
        }

class FeeChallanPaymentSerializer(serializers.Serializer):
    paid = serializers.FloatField()
    discount = serializers.FloatField()
