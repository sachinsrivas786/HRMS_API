from rest_framework import serializers
from .models import ApplicationDetails, InterviewDetails, InterviewResponse, RejectReviewAllotment, RevokedToken, TestScheduleDetails, VacancyDetails,candidate_details

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDetails
        fields = ['candidate__name', 'candidate__email', 'candidate__mobile_no', 'candidate_id', 'application_id', 'position_shortlisted_for', 'branch_shortlisted_for']
        
        
# class CandidateDetailsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = candidate_details
#         fields = ['id', 'name', 'email', 'mobile_no']

# class ApplicationDetailsSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = ApplicationDetails
#         fields = ['id', 'candidate', 'position_shortlisted_for']

# class ScheduledUserDetailsSerializer(serializers.Serializer):
#     is_hr = serializers.BooleanField()
#     is_hrhead = serializers.BooleanField()
#     applicants = serializers.ListField(child=CandidateDetailsSerializer())
#     distinct_positions = serializers.ListField(child=serializers.CharField())
#     applicants1 = serializers.ListField(child=ApplicationDetailsSerializer())
#     distinct_positions1 = serializers.ListField(child=serializers.CharField())

class ScheduledUserDetailsSerializer(serializers.Serializer):
    candidate_id = serializers.IntegerField()
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    mobile_no = serializers.CharField(max_length=15)
    position_shortlisted_for = serializers.CharField(max_length=255)

    def to_representation(self, instance):
        return {
            'candidate_id': instance[3],  # Accessing the fourth element of the tuple (0-indexed)
            'id': instance[4],            # Accessing the fifth element of the tuple
            'name': instance[0],          # Accessing the first element of the tuple
            'email': instance[1],         # Accessing the second element of the tuple
            'mobile_no': instance[2],     # Accessing the third element of the tuple
            'position_shortlisted_for': instance[5]  # Accessing the sixth element of the tuple
        }


class ApplicantSerializer1(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDetails
        fields = ('application_id', 'position_shortlisted_for', 'branch_shortlisted_for', 'candidate')

    candidate = serializers.SerializerMethodField()

    def get_candidate(self, obj):
        try:
            candidate_obj = candidate_details.objects.get(id=obj.candidate_id)
            return {
                'name': candidate_obj.name,
                'email': candidate_obj.email,
                'mobile_no': candidate_obj.mobile_no
            }
        except candidate_details.DoesNotExist:
            return None
        
class VacancyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacancyDetails
        fields = '__all__'
        
class InterviewDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewDetails
        fields = '__all__'  # Include all fields in the serializer
        
class ApplicationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDetails
        fields = '__all__'
        
class CandidateDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidate_details
        fields = '__all__'

class InterviewResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewResponse
        fields = '__all__'
        
class TestScheduleDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestScheduleDetails
        fields = '__all__'
        
class CandidateDetailsSerializer1(serializers.ModelSerializer):
    class Meta:
        model = candidate_details
        fields = ['id', 'name', 'email', 'mobile_no']
        
class NumberOfInterviewerSerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    data_num = serializers.IntegerField()
    success = serializers.CharField(max_length=255)
    

class OnboardingCandidatesSerializer(serializers.ModelSerializer):
    candidate = CandidateDetailsSerializer(source='candidate_id', read_only=True)

    class Meta:
        model = ApplicationDetails
        fields = ['candidate', 'application_id', 'position_shortlisted_for', 'branch_shortlisted_for']


# class AssessedCandidatesSerializer(serializers.Serializer):
#     candidate = CandidateDetailsSerializer()
#     application = ApplicationDetailsSerializer()
#     interview_response = InterviewResponseSerializer()
#     interview = InterviewDetailsSerializer()
#     interview_score = serializers.FloatField(allow_null=True)

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
        
#         # Check if 'candidate' key exists in the instance
#         if 'candidate' in instance:
#             data['id'] = instance['candidate']['id']
#         else:
#             data['id'] = None  # Set default value or handle the case accordingly
        
#         # Check if 'application' key exists in the instance
#         if 'application' in instance:
#             data['position_shortlisted_for'] = instance['application']['position_shortlisted_for']
#             data['branch_shortlisted_for'] = instance['application']['branch_shortlisted_for']
#         else:
#             data['position_shortlisted_for'] = None  # Set default value or handle the case accordingly
#             data['branch_shortlisted_for'] = None  # Set default value or handle the case accordingly
        
#         return data
class AssessedCandidatesSerializer(serializers.Serializer):
    interview_details = InterviewDetailsSerializer()
    application_details = ApplicationDetailsSerializer()
    interview_responses = InterviewResponseSerializer(many=True)

class ApplicationDetailsSerializer1(serializers.ModelSerializer):
    interview_details = InterviewDetailsSerializer()
    interview_responses = InterviewResponseSerializer(many=True)

    class Meta:
        model = ApplicationDetails
        fields = ['interview_details', 'application_details', 'interview_responses']
        
class RescheduleInterviewUserSerializer(serializers.Serializer):
    application_id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    mobile_no = serializers.CharField()
    interview_date = serializers.DateTimeField()
    candidate_id = serializers.IntegerField()
    
class RejectReviewAllotmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectReviewAllotment
        fields = '__all__'
        
class ApplicationDetailsSerializer2(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDetails
        fields = ['branch_shortlisted_for', 'position_shortlisted_for', 'application_status']

class CandidateSerializer(serializers.ModelSerializer):
    application_details = ApplicationDetailsSerializer(many=True, read_only=True)

    class Meta:
        model = candidate_details
        fields = ['name', 'email', 'mobile_no', 'application_details']
        
class SignUpSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    pass1 = serializers.CharField(max_length=128)
    pass2 = serializers.CharField(max_length=128)
    name = serializers.CharField(max_length=150)
    dob = serializers.DateField()
    mob = serializers.CharField(max_length=15)
    gender = serializers.CharField(max_length=10)
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    pass1 = serializers.CharField(max_length=128)
    
    
class RevokedTokenSerializer(serializers.ModelSerializer):
	class Meta:
		model = RevokedToken
		fields ='__all__'