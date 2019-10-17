from rest_framework import serializers

from accounts import models
from structure import models as structure_models

class JWTUserDetailsSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = obj['user']
        data = {
            'id': user.id,
            'username': user.username,
            'role': user.profile.get_profile_type_display(),
            'fullname': user.profile.fullname
        }
        return data


class TeacherAutocompleteSerializer(serializers.ModelSerializer):

    fullname = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = ('id', 'fullname', )

    def get_fullname(self, instance):
        return instance.profile.fullname


class StudentProfileSerializer(serializers.ModelSerializer):

    gr_number = serializers.SerializerMethodField()

    class Meta:
        model = models.Profile
        fields = ('id', 'fullname', 'gr_number', 'user_id')

    def get_gr_number(self, obj):
        try:
            return obj.student_info.gr_number
        except:
            return None


class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('id', 'fullname', 'user_id')


class StaffSerializer(serializers.ModelSerializer):
    profile = StaffProfileSerializer(read_only=True)

    class Meta:
        model = models.User
        fields = ('id', 'profile')


class StudentSerializer(serializers.ModelSerializer):
    profile = StudentProfileSerializer(read_only=True)
    class Meta:
        model = models.User
        fields = ('id', 'profile')


class CreateUpdateStudentSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=False)
    fullname = serializers.CharField(max_length=128)
    gr_number = serializers.CharField(max_length=20)
    date_of_birth = serializers.DateField()
    date_enrolled = serializers.DateField()
    address = serializers.CharField(max_length=128)
    grade_id = serializers.IntegerField()
    section_id = serializers.IntegerField()
    guardian_name = serializers.CharField(max_length=128)
    guardian_contact = serializers.CharField(max_length=20)
    gender = serializers.IntegerField()

    def validate_user(self, value):
        if self.context['update'] and value is None:
            raise serializers.ValidationError("User id is required while updating user.")
        if value:
            user = models.User.objects.filter(
                id=value, is_active=True
            ).select_related('profile__student_info').first()
            if user:
                return user
            else:
                raise serializers.ValidationError("Invalid user id.")
        return value

    def validate_gr_number(self, value):
        if not self.context['update'] and models.User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Roll number already assigned.")
        else:
            return value

    def validate_gender(self, value):
        if value in [models.MALE, models.FEMALE]:
            return value
        else:
            raise serializers.ValidationError('Invalid gender.')

    def validate_section_id(self, value):
        try:
            structure_models.Section.objects.get(id=value)
            return value
        except:
            raise serializers.ValidationError("Invalid section id.")

    def save(self, **kwargs):
        if self.context['update']:
            self.update_user()
        else:
            self.create_user()        

    def create_user(self):
        validated_data = self.validated_data
        user = models.User(username=validated_data['gr_number'])
        user.set_password(validated_data['gr_number'])
        user.is_active = True
        user.save()
        # Create student info
        info = models.StudentInfo(
            gr_number=validated_data['gr_number'],
            section_id=validated_data['section_id'],
            date_enrolled=validated_data['date_enrolled'],
            date_of_birth=validated_data['date_of_birth'],
            address=validated_data['address'],
            guardian_name=validated_data['guardian_name'],
            guardian_contact=validated_data['guardian_contact'],
            gender=validated_data['gender']
        )
        info.save()
        # Create profile
        profile = models.Profile(
            user_id=user.id, fullname=validated_data['fullname'],
            student_info_id=info.id, profile_type=models.Profile.STUDENT
        )
        profile.save()

    def update_user(self):
        validated_data = self.validated_data
        user = validated_data['user']
        profile = user.profile
        # update student info
        info = profile.student_info
        info.gr_number = validated_data['gr_number']
        info.section_id = validated_data['section_id']
        info.date_enrolled = validated_data['date_enrolled']
        info.date_of_birth = validated_data['date_of_birth']
        info.address = validated_data['address']
        info.guardian_name = validated_data['guardian_name']
        info.guardian_contact = validated_data['guardian_contact']
        info.gender = validated_data['gender']
        info.save()
        # update profile
        profile.fullname = validated_data['fullname']
        profile.save()


class CreateUpdateStaffSerializer(serializers.Serializer):
    user = serializers.IntegerField(required=False)
    fullname = serializers.CharField(max_length=128)
    date_hired = serializers.DateField()
    contact = serializers.CharField(max_length=128)
    gender = serializers.IntegerField()
    address = serializers.CharField(max_length=128)

    def validate_user(self, value):
        if self.context['update'] and value is None:
            raise serializers.ValidationError("User id is required while updating user.")
        if value:
            user = models.User.objects.filter(
                id=value, is_active=True
            ).select_related('profile__staff_info').first()
            if user:
                return user
            else:
                raise serializers.ValidationError("Invalid user id.")
        return value

    def validate_gender(self, value):
        if value in [models.MALE, models.FEMALE]:
            return value
        else:
            raise serializers.ValidationError('Invalid gender.')

    def save(self, **kwargs):
        if self.context['update']:
            self.update_user()
        else:
            self.create_user()

    def create_user(self):
        validated_data = self.validated_data
        user = models.User(username=validated_data['fullname'].replace(' ', ''))
        user.set_password(validated_data['fullname'].replace(' ', ''))
        user.is_active = True
        user.save()
        # Create student info
        info = models.StaffInfo(
            date_hired=validated_data['date_hired'],
            address=validated_data['address'],
            gender=validated_data['gender'],
        )
        info.save()
        # Create profile
        profile = models.Profile(
            user_id=user.id, fullname=validated_data['fullname'],
            contact=validated_data['contact'],
            staff_info_id=info.id, profile_type=models.Profile.STAFF
        )
        profile.save()

    def update_user(self):
        validated_data = self.validated_data
        user = validated_data['user']
        profile = user.profile
        # update staff info
        info = profile.staff_info
        info.date_hired = validated_data['date_hired']
        info.address = validated_data['address']
        info.gender = validated_data['gender']
        info.save()
        # update profile
        profile.fullname = validated_data['fullname']
        profile.contact = validated_data['contact']
        profile.save()


class StudentFilterSerializer(serializers.Serializer):
    grade_id = serializers.IntegerField()
    section_id = serializers.IntegerField(required=False)
    search_term = serializers.CharField(max_length=128, required=False)
    page = serializers.IntegerField(allow_null=True, required=False)


class StaffFilterSerializer(serializers.Serializer):
    search_term = serializers.CharField(max_length=128, required=False)
    page = serializers.IntegerField(allow_null=True, required=False)


class StudentInfoSerializer(serializers.ModelSerializer):
    section = serializers.SerializerMethodField()
    class Meta:
        model = models.StudentInfo
        fields = (
            'gr_number', 'section', 'date_enrolled', 'date_of_birth',
            'address', 'guardian_name', 'guardian_contact', 'gender',
        )
    
    def get_section(self, obj):
        try:
            section = obj.section
            return {
                'id': section.id,
                'name': section.name,
                'grade_id': section.grade_id,
                'grade_name': section.grade.name,
            }
        except:
            return None


class StaffInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StaffInfo
        fields = (
            'date_hired', 'salary', 'designation', 'address', 'gender'
        )


class StudentDetailsSerializer(serializers.ModelSerializer):
    student_info = StudentInfoSerializer(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Profile
        fields = (
            'id', 'fullname', 'student_info'
        )

    def get_id(self, obj):
        return obj.user_id


class StaffDetailsSerializer(serializers.ModelSerializer):
    staff_info = StaffInfoSerializer(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = models.Profile
        fields = (
            'id', 'fullname', 'contact', 'staff_info'
        )

    def get_id(self, obj):
        return obj.user_id
