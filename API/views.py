from django.http import JsonResponse
from django.shortcuts import render
from pikepdf import Permissions
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from .models import ApplicationDetails, Document_Candidate, InterviewDetails, InterviewResponse, OfferLetter, RejectReviewAllotment, RevokedToken, TestScheduleDetails, Token, User_Rolls, VacancyDetails, Verification_Document,  candidate_details
from datetime import datetime
from .serializers import ApplicantSerializer, ApplicantSerializer1, ApplicationDetailsSerializer, CandidateDetailsSerializer, CandidateDetailsSerializer1, CandidateSerializer, InterviewDetailsSerializer, InterviewResponseSerializer, LoginSerializer, NumberOfInterviewerSerializer, OnboardingCandidatesSerializer, RejectReviewAllotmentSerializer, RescheduleInterviewUserSerializer, ScheduledUserDetailsSerializer, SignUpSerializer, TestScheduleDetailsSerializer, VacancyDetailsSerializer
from sqlalchemy import create_engine
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication
from django.utils.crypto import get_random_string

user1 = "SFPL_Connect"
password = "$%n5bF33%X"
db = "Sonata_ConnectHR"
server = "172.17.130.216"
engine = create_engine(f"mssql+pyodbc://{user1}:{password}@{server}/{db}?driver=ODBC+Driver+17+for+SQL+Server")
cursor = connection.cursor()

from django.middleware.csrf import get_token

# class CsrfExemptSessionAuthentication(SessionAuthentication):
#     def enforce_csrf(self, request):
#         return  # To not perform the CSRF check previously happening
    
from rest_framework_simplejwt.tokens import RefreshToken
# Generate Token Manually
# def get_tokens_for_user(user):
#   refresh = RefreshToken.for_user(user)
#   return {
#       'refresh': str(refresh),
#       'access': str(refresh.access_token),
#   }

# @method_decorator(csrf_exempt, name='dispatch')
# class SignUpAPIView(APIView):

#     def post(self, request, format=None):

#         serializer = SignUpSerializer(data=request.data)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#             username = validated_data.get('user')
#             email = validated_data.get('email')
#             pass1 = validated_data.get('pass1')
#             pass2 = validated_data.get('pass2')
#             name = validated_data.get('name')
#             dob = validated_data.get('dob')
#             mob = validated_data.get('mob')
#             gender = validated_data.get('gender')

#             if pass1 != pass2:
#                 return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

#             try:
#                 myuser = User.objects.create_user(username, email, pass1)
                
#                 user = serializer.save()
#                 # user = request.user
#                 print('user_id',user.id)
#                 token = get_tokens_for_user(user)
#                 revoked_token = Token.objects.create(token=token,user_id = user.id)
#                 revoked_token.save()
                        
#                 candidate_profile, created = candidate_details.objects.get_or_create(email=email)
#                 if created:
#                     candidate_profile.name = name
#                     candidate_profile.gender = gender
#                     candidate_profile.dob = dob
#                     candidate_profile.mobile_no = mob
#                     candidate_profile.save()

#                 user_roll = User_Rolls(user_id=myuser.id, roll_id=0)
#                 user_roll.save()

#                 doc = Document_Candidate(candidate_id=candidate_profile.id)
#                 doc.save()

#                 verify = Verification_Document(candidate_id=candidate_profile.id)
#                 verify.save()

#                 letter = OfferLetter(candidate_id=candidate_profile.id)
#                 letter.save()
                
 

#                 return Response({"token":token,"message": "Your account has been successfully created"}, status=status.HTTP_201_CREATED)

#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_token(user):
    token, created = Token.objects.get_or_create(user_id=user.id)
    return token

def save_token(user, token):
    try:
        revoked_token = Token.objects.get(user_id=user.id)
        revoked_token.token = token.token
        revoked_token.save()
    except Token.DoesNotExist:
        Token.objects.create(user=user, token=token.token)

@method_decorator(csrf_exempt, name='dispatch')
class SignUpAPIView(APIView):

    def post(self, request, format=None):

        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                validated_data = serializer.validated_data
                username = validated_data.get('user')
                email = validated_data.get('email')
                pass1 = validated_data.get('pass1')
                pass2 = validated_data.get('pass2')
                name = validated_data.get('name')
                dob = validated_data.get('dob')
                mob = validated_data.get('mob')
                gender = validated_data.get('gender')

                if pass1 != pass2:
                    return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

                user = User.objects.create_user(username=username, email=email, password=pass1)

                token = generate_token(user)
                save_token(user, token)

                candidate_profile, created = candidate_details.objects.get_or_create(email=email)
                if created:
                    candidate_profile.name = name
                    candidate_profile.gender = gender
                    candidate_profile.dob = dob
                    candidate_profile.mobile_no = mob
                    candidate_profile.save()

                user_roll = User_Rolls.objects.create(user_id=user.id, roll_id=0)
                user_roll.save()

                doc = Document_Candidate.objects.create(candidate_id=candidate_profile.id)
                doc.save()
                verify = Verification_Document.objects.create(candidate_id=candidate_profile.id)
                verify.save()
                letter = OfferLetter.objects.create(candidate_id=candidate_profile.id)
                letter.save()
                return Response({"token": token.token, "message": "Your account has been successfully created", "user_id": user.id}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user:
            # Generate token for the authenticated user
            tok, _ = Token.objects.get_or_create(user_id=user.id)
            token_key = tok.token

            # Return token and success message
            return Response({'token': token_key, 'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            # Return error message if authentication fails
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)        
                
class SignInAPIView(APIView):
    def get(self, request):
        next_param = request.GET.get('next')
        request.session['next_param'] = next_param
        return Response({"message": "Sign-in page rendered"}, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    def post(self, request):
        # Retrieve the user's token from the request headers
        token_value = request.headers.get('Authorization')

        # Check if the token exists
        try:
            token = Token.objects.get(token=token_value)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Delete the token
        token.delete()

        # Return a success message
        return Response({'message': 'Logout successful'})    
# Create your views here.
# class ScheduleOnlineTestAPIView(APIView):
#     def get(self, request):
#         response_data = {'success': False, 'message': 'Error in retrieving data'}

#         try:
#             applicants_2 = ApplicationDetails.objects.filter(application_status=2)
#             applicants_1 = ApplicationDetails.objects.filter(application_status=3)

#             data_2 = []
#             for applicant in applicants_2:
#                 candidate = candidate_details.objects.get(id=applicant.candidate_id)
#                 data_2.append({
#                     'name': candidate.name,
#                     'email': candidate.email,
#                     'mobile_no': candidate.mobile_no,
#                     'candidate_id': candidate.id,
#                     'application_id': applicant.application_id,
#                     'position_shortlisted_for': applicant.position_shortlisted_for,
#                     'branch_shortlisted_for': applicant.branch_shortlisted_for,
#                 })

#             data_1 = []
#             for applicant in applicants_1:
#                 candidate = candidate_details.objects.get(id=applicant.candidate_id)
#                 data_1.append({
#                     'name': candidate.name,
#                     'email': candidate.email,
#                     'mobile_no': candidate.mobile_no,
#                     'candidate_id': candidate.id,
#                     'application_id': applicant.application_id,
#                     'position_shortlisted_for': applicant.position_shortlisted_for,
#                     'branch_shortlisted_for': applicant.branch_shortlisted_for,
#                 })

#             response_data = {
#                 'success': True,
#                 'applicants_2': data_2,
#                 'applicants_1': data_1
#             }
#         except Exception as e:
#             response_data['message'] = str(e)

#         return Response(response_data)
    
class ScheduleOnlineTestAPIView(APIView):
    def get(self, request):
        response_data = {'success': False, 'message': 'Error in retrieving data'}

        try:
            applicants_2 = ApplicationDetails.objects.filter(application_status=2)
            applicants_1 = ApplicationDetails.objects.filter(application_status=3)

            serializer_2 = ApplicantSerializer1(applicants_2, many=True)
            serializer_1 = ApplicantSerializer1(applicants_1, many=True)

            response_data = {
                'success': True,
                'applicants_2': serializer_2.data,
                'applicants_1': serializer_1.data
            }
        except Exception as e:
            response_data['message'] = str(e)

        return Response(response_data)
   

def ScheduleOnlineTest(request):
    try:
        # Make a GET request to the API endpoint
        response = requests.get('http://127.0.0.1:8000/api/user/ScheduleOnlineTestAPIView/')
        response.raise_for_status()  # Raise an exception for non-200 status codes
        
        # Extract data from the response
        data = response.json()
        
        # Extract applicants data from the response
        applicants_1 = data.get('applicants_1', [])
        applicants_2 = data.get('applicants_2', [])
        
        # Pass the applicants data to the template for rendering
        return render(request, 'schedule_test_userdetails.html', {'applicants_1': applicants_1, 'applicants_2': applicants_2})
    
    except requests.RequestException as e:
        # Handle request exceptions (e.g., network errors)
        error_message = f'Error fetching data from API: {e}'
        return render(request, 'schedule_test_userdetails.html', {'error_message': error_message})
        
 
# def sceduled_user_details(request):
#     is_hr=False
#     is_hrhead = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#         except:
#             pass
#     query = f"""SELECT cd.name, cd.email, cd.mobile_no, cd.id as candidate_id, ad.application_id as id, ad.position_shortlisted_for FROM application_details ad 
#                 LEFT JOIN candidate_details cd 
#                 ON ad.candidate_id = cd.id 
#                 WHERE ad.application_status = 4 """
    
#     applicants = pd.read_sql(query, engine)
    
#     print(applicants)
#     distinct_positions_queryset = applicants[['position_shortlisted_for']].drop_duplicates(keep='first')
#     distinct_positions_queryset.dropna(inplace=True)
#     distinct_positions = distinct_positions_queryset['position_shortlisted_for'].tolist()
#     print(distinct_positions)
#     applicants=applicants.to_dict('records')
    
    
#     query = f"""SELECT cd.name, cd.email, cd.mobile_no, cd.id as candidate_id, ad.application_id as id, ad.position_shortlisted_for FROM application_details ad 
#             LEFT JOIN candidate_details cd 
#             ON ad.candidate_id = cd.id 
#             WHERE ad.application_status = 5"""
    
#     applicants1 = pd.read_sql(query, engine)
    
#     print(applicants)
#     distinct_positions_queryset = applicants1[['position_shortlisted_for']].drop_duplicates(keep='first')
#     distinct_positions_queryset.dropna(inplace=True)
#     distinct_positions1 = distinct_positions_queryset['position_shortlisted_for'].tolist()
#     print(distinct_positions1)
#     applicants1=applicants1.to_dict('records')
    
#     return render(request, 'sceduledUserDetails.html',{'is_hr':is_hr ,'is_hrhead':is_hrhead,'applicants':applicants,'distinct_positions':distinct_positions,'distinct_positions1':distinct_positions1,'applicants1':applicants1 })
# class ScheduledUserDetailsAPIView(APIView):
#     def get(self, request):
#         is_hr = False
#         is_hrhead = False
#         response_data = {}

#         if request.user.is_authenticated:
#             user_id = request.user.id
#             try:
#                 user_roll = User_Rolls.objects.get(user_id=user_id)
#                 is_hr = True if user_roll.roll_id == 1 else False
#                 is_hrhead = True if user_roll.roll_id == 3 else False
#             except User_Rolls.DoesNotExist:
#                 pass
        
#         query = """SELECT cd.name, cd.email, cd.mobile_no, cd.id as candidate_id, ad.application_id as id, ad.position_shortlisted_for 
#                    FROM application_details ad 
#                    LEFT JOIN candidate_details cd 
#                    ON ad.candidate_id = cd.id 
#                    WHERE ad.application_status = 4 """
        
#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             applicants = cursor.fetchall()

#         distinct_positions = list(set([applicant[5] for applicant in applicants if applicant[5]]))

#         query = """SELECT cd.name, cd.email, cd.mobile_no, cd.id as candidate_id, ad.application_id as id, ad.position_shortlisted_for 
#                    FROM application_details ad 
#                    LEFT JOIN candidate_details cd 
#                    ON ad.candidate_id = cd.id 
#                    WHERE ad.application_status = 5"""
        
#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             applicants1 = cursor.fetchall()

#         distinct_positions1 = list(set([applicant[5] for applicant in applicants1 if applicant[5]]))

#         response_data = {
#             'is_hr': is_hr,
#             'is_hrhead': is_hrhead,
#             'applicants': applicants,
#             'distinct_positions': distinct_positions,
#             'applicants1': applicants1,
#             'distinct_positions1': distinct_positions1
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

class ScheduledUserDetailsAPIView(APIView):
    def get(self, request):
        is_hr = False
        is_hrhead = False

        if request.user.is_authenticated:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = True if user_roll.roll_id == 1 else False
                is_hrhead = True if user_roll.roll_id == 3 else False
            except User_Rolls.DoesNotExist:
                pass

        query1 = """
            SELECT cd.name, cd.email, cd.mobile_no, cd.id as candidate_id, ad.application_id as id, ad.position_shortlisted_for 
            FROM application_details ad 
            LEFT JOIN candidate_details cd 
            ON ad.candidate_id = cd.id 
            WHERE ad.application_status = 4
        """

        query2 = """
            SELECT cd.name, cd.email, cd.mobile_no, cd.id as candidate_id, ad.application_id as id, ad.position_shortlisted_for 
            FROM application_details ad 
            LEFT JOIN candidate_details cd 
            ON ad.candidate_id = cd.id 
            WHERE ad.application_status = 5
        """

        with connection.cursor() as cursor:
            cursor.execute(query1)
            applicants1 = cursor.fetchall()

            cursor.execute(query2)
            applicants2 = cursor.fetchall()

        serializer1 = ScheduledUserDetailsSerializer(applicants1, many=True)
        serializer2 = ScheduledUserDetailsSerializer(applicants2, many=True)

        response_data = {
            'is_hr': is_hr,
            'is_hrhead': is_hrhead,
            'applicants1': serializer1.data,
            'applicants2': serializer2.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

# def hold_user_details(request):
#     is_hr=False
#     is_hrhead = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#         except:
#             pass
#         query = """
#         SELECT 
#             cd.name, 
#             cd.email, 
#             cd.mobile_no, 
#             cd.id as candidate_id, 
#             ad.application_id,
#             ad.position_shortlisted_for,
#             ad.branch_shortlisted_for
            
#         FROM application_details ad 
#         LEFT JOIN candidate_details cd ON ad.candidate_id = cd.id 
#         WHERE ad.application_status = 11
#     """
    
#         df = pd.read_sql(query, engine)
#         print(df, "data")

#         data_list = df.to_dict(orient='records')
#         print(data_list)

#         applicants = ApplicationDetails.objects.filter(application_status=11)
#         candidate = candidate_details.objects.all()  
#         distinct_positions_queryset = applicants.values_list("position_shortlisted_for", flat=True).distinct()
#         distinct_positions = [position for position in distinct_positions_queryset if position is not None]
#         print(distinct_positions)
#         context = {
#             'applicants': applicants,
#             'candidates': candidate,
#             'distinct_positions': distinct_positions,
#             'data_list': data_list,
#             'is_hr':is_hr ,'is_hrhead':is_hrhead,
#         }
#         return render(request, 'holdUserDetails.html', context)

# class HoldUserDetailsAPIView(APIView):
#     def get(self, request):
#         is_hr = False
#         is_hrhead = False
#         response_data = {}

#         if request.user.is_authenticated:
#             user_id = request.user.id
#             try:
#                 user_roll = User_Rolls.objects.get(user_id=user_id)
#                 is_hr = True if user_roll.roll_id == 1 else False
#                 is_hrhead = True if user_roll.roll_id == 3 else False
#             except User_Rolls.DoesNotExist:
#                 pass

#         query = """
#             SELECT 
#                 cd.name, 
#                 cd.email, 
#                 cd.mobile_no, 
#                 cd.id as candidate_id, 
#                 ad.application_id,
#                 ad.position_shortlisted_for,
#                 ad.branch_shortlisted_for
#             FROM application_details ad 
#             LEFT JOIN candidate_details cd ON ad.candidate_id = cd.id 
#             WHERE ad.application_status = 11
#         """

#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             applicants = cursor.fetchall()

#         distinct_positions_queryset = ApplicationDetails.objects.filter(application_status=11).values_list("position_shortlisted_for", flat=True).distinct()
#         distinct_positions = list(set([position for position in distinct_positions_queryset if position]))

#         response_data = {
#             'is_hr': is_hr,
#             'is_hrhead': is_hrhead,
#             'applicants': applicants,
#             'distinct_positions': distinct_positions
#         }

#         return Response(response_data, status=status.HTTP_200_OK)
class HoldUserDetailsAPIView(APIView):
    def get(self, request):
        is_hr = False
        is_hrhead = False

        if request.user.is_authenticated:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = user_roll.roll_id == 1
                is_hrhead = user_roll.roll_id == 3
            except User_Rolls.DoesNotExist:
                pass

        applicants = ApplicationDetails.objects.filter(application_status=11)
        serializer = ApplicantSerializer(applicants, many=True)

        distinct_positions_queryset = ApplicationDetails.objects.filter(application_status=11).values_list("position_shortlisted_for", flat=True).distinct()
        distinct_positions = list(set([position for position in distinct_positions_queryset if position]))

        response_data = {
            'is_hr': is_hr,
            'is_hrhead': is_hrhead,
            'applicants': serializer.data,
            'distinct_positions': distinct_positions
        }

        return Response(response_data)

# def vacancy_lists(request):
#     is_hr=False
#     is_hrhead = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#         except:
#             pass
#     # Open Vacancies
#     sql_query = f"""
#     SELECT * FROM VACANCY_DETAILS vd 
#     LEFT JOIN INTERVIEW_DETAILS id ON vd.vacancy_id = id.vacancy_id 
#     where walk_in_id = 0
#     order by vacancy_date desc
#                 """
#     vacancies = pd.read_sql_query(sql_query, engine)
#     print(';;;;;;;;;;;;;;;;;;;')
#     print(vacancies)
    
#     if not vacancies.empty:
#         vacancies['vacancy_date'] = vacancies['vacancy_date'].dt.strftime('%d-%m-%Y')
#         vacancies['interview_date'] = vacancies['interview_date'].dt.strftime('%d-%m-%Y')

#         print(str(request.user))
#         print(type(str(request.user)))
#         distinct_positions = vacancies[['role']]['role'].unique().tolist()
#         print(vacancies)
#         today = datetime.today().date()
#         # vacancies = vacancies.sort_values(by=['vacancy_date'], ascending=False, inplace=True)
#         vacancies.drop_duplicates(subset="vacancy_id", keep="first", inplace=True)
#         vacancies.drop_duplicates(keep="first", inplace=True)
#         vacancies = vacancies.to_dict("records")
#         vacancy_list = InterviewDetails.objects.filter(interview_date__gt=today).values_list('vacancy_id')
#         vacancies = VacancyDetails.objects.filter(vacancy_id__in = vacancy_list,walk_in_id = 0).order_by('-vacancy_date')                 

#         pprint.pprint(vacancies)

#         data = []
#         for i in vacancies:
#             d = {}
#             d['id']=i.vacancy_id
#             d['walk_in_id']=i.walk_in_id if i.walk_in_id else "-"
#             d['branch_name']=i.branch if i.branch else "-"
#             d['required_skills']=i.required_skills.split(",") if i.required_skills else []
#             d['job_role']=i.role if i.role else "-"
#             d['no_of_vacancies']=i.capacity if i.capacity else "-"
#             d['qualification_type']=i.qualification if i.qualification else "-"
#             d['required_experience']=i.required_experience if i.required_experience else "-"
#             d['salary']=i.salary if i.salary else "-"
#             d['vacancy_date']=i.vacancy_date if i.vacancy_date else "-"
#             # d['interview_date'] = i.interview_date if i.interview_date else "-"
#             data.append(d)
#     else:
#         data = []
#         distinct_positions = []
#     # Closed Vacancies
#     sql_query = f"""
#     SELECT * FROM VACANCY_DETAILS vd 
#     LEFT JOIN INTERVIEW_DETAILS id ON vd.vacancy_id = id.vacancy_id 
#     where walk_in_id = 0 or walk_in_id = 1
#     order by vacancy_date desc
#                 """
#     vacancies = pd.read_sql_query(sql_query, engine)
#     print(vacancies)
#     if not vacancies.empty:
#         vacancies['vacancy_date'] = vacancies['vacancy_date'].dt.strftime('%d-%m-%Y')
#         vacancies['interview_date'] = vacancies['interview_date'].dt.strftime('%d-%m-%Y')

#         print(str(request.user))
#         print(type(str(request.user)))
#         distinct_positions = vacancies[['role']]['role'].unique().tolist()
#         print(vacancies)
#         # vacancies = vacancies.sort_values(by=['vacancy_date'], ascending=False, inplace=True)
#         vacancies.drop_duplicates(subset="vacancy_id", keep="first", inplace=True)
#         vacancies.drop_duplicates(keep="first", inplace=True)
#         vacancies = vacancies.to_dict("records")
#         vacancy_list = InterviewDetails.objects.filter(interview_date__lte=today).values_list('vacancy_id')
#         vacancies = VacancyDetails.objects.filter(vacancy_id__in = vacancy_list).order_by('-vacancy_date')
#         pprint.pprint(vacancies)

#         data2 = []
#         for i in vacancies:
#             e = {}
#             e['id']=i.vacancy_id
#             e['walk_in_id']=i.walk_in_id if i.walk_in_id else "-"
#             e['branch_name']=i.branch if i.branch else "-"
#             e['required_skills']=i.required_skills.split(",") if i.required_skills else []
#             e['job_role']=i.role if i.role else "-"
#             e['no_of_vacancies']=i.capacity if i.capacity else "-"
#             e['qualification_type']=i.qualification if i.qualification else "-"
#             e['required_experience']=i.required_experience if i.required_experience else "-"
#             e['salary']=i.salary if i.salary else "-"
#             e['vacancy_date']=i.vacancy_date if i.vacancy_date else "-"
#             # d['interview_date'] = i.interview_date if i.interview_date else "-"
#             data2.append(e)
#     else:
#         data2 = []
#         distinct_positions = []
    
#         #for walk-in positions 
#     sql_query = f"""
#     SELECT * FROM VACANCY_DETAILS vd 
#     LEFT JOIN INTERVIEW_DETAILS id ON vd.vacancy_id = id.vacancy_id 
#     where walk_in_id = 1
#     order by vacancy_date desc
#                 """
#     vacancies1 = pd.read_sql_query(sql_query, engine)
#     vacancy_list = []
#     print('vacancies1',vacancies1)
#     if not vacancies1.empty:
#         vacancies1['vacancy_date'] = vacancies1['vacancy_date'].dt.strftime('%d-%m-%Y')
#         vacancies1['interview_date'] = vacancies1['interview_date'].dt.strftime('%d-%m-%Y')
#         print(str(request.user))
#         print(type(str(request.user)))
#         distinct_positions = vacancies1[['role']]['role'].unique().tolist()
#         print(vacancies1)
#         # vacancies = vacancies.sort_values(by=['vacancy_date'], ascending=False, inplace=True)
#         vacancies1.drop_duplicates(subset="vacancy_id", keep="first", inplace=True)
#         vacancies1.drop_duplicates(keep="first", inplace=True)
#         vacancies1 = vacancies1.to_dict("records")
#         vacancy_list = InterviewDetails.objects.filter(interview_date__gt=today).values_list('vacancy_id')
#         vacancies1 = VacancyDetails.objects.filter(vacancy_id__in = vacancy_list,walk_in_id=1).order_by('-vacancy_date')
#         pprint.pprint(vacancies1)

#         data1 = []
#         for i in vacancies1:
#             k = {}
#             k['id']=i.vacancy_id
#             k['walk_in_id']=i.walk_in_id if i.walk_in_id else "-"
#             k['branch_name']=i.branch if i.branch else "-"
#             k['required_skills']=i.required_skills.split(",") if i.required_skills else []
#             k['job_role']=i.role if i.role else "-"
#             k['no_of_vacancies']=i.capacity if i.capacity else "-"
#             k['qualification_type']=i.qualification if i.qualification else "-"
#             k['required_experience']=i.required_experience if i.required_experience else "-"
#             k['salary']=i.salary if i.salary else "-"
#             k['vacancy_date']=i.vacancy_date if i.vacancy_date else "-"
#             # k['interview_date'] = i.interview_date if i.interview_date else "-"
#             data1.append(k)
#     else:
#         data1 = []
#         distinct_positions = []
   
#     pprint.pprint(data)
#     context = {'vacancy':data,'vacancy1':data1,'vacancy2':data2, 'distinct_positions':distinct_positions,'is_hr':is_hr ,'is_hrhead':is_hrhead}    
#     return render(request,'vacancy_lists.html',context)

# class VacancyListsAPIView(APIView):
#     def get(self, request):
#         is_hr = False
#         is_hrhead = False
#         response_data = {}

#         # Check if the user is authenticated
#         if request.user.is_authenticated:
#             user_id = request.user.id
#             try:
#                 user_roll = User_Rolls.objects.get(user_id=user_id)
#                 is_hr = user_roll.roll_id == 1
#                 is_hrhead = user_roll.roll_id == 3
#             except User_Rolls.DoesNotExist:
#                 pass

#         today = datetime.today().date()

#         # Fetch open vacancies
#         open_vacancies = VacancyDetails.objects.filter(walk_in_id=0).order_by('-vacancy_date')

#         open_vacancies_data = []
#         for vacancy in open_vacancies:
#             vacancy_data = {
#                 'id': vacancy.vacancy_id,
#                 'walk_in_id': vacancy.walk_in_id if vacancy.walk_in_id else "-",
#                 'branch_name': vacancy.branch if vacancy.branch else "-",
#                 'required_skills': vacancy.required_skills.split(",") if vacancy.required_skills else [],
#                 'job_role': vacancy.role if vacancy.role else "-",
#                 'no_of_vacancies': vacancy.capacity if vacancy.capacity else "-",
#                 'qualification_type': vacancy.qualification if vacancy.qualification else "-",
#                 'required_experience': vacancy.required_experience if vacancy.required_experience else "-",
#                 'salary': vacancy.salary if vacancy.salary else "-",
#                 'vacancy_date': vacancy.vacancy_date.strftime('%d-%m-%Y') if vacancy.vacancy_date else "-",
#             }
#             open_vacancies_data.append(vacancy_data)

#         # Fetch closed vacancies
#         closed_vacancies = VacancyDetails.objects.filter(walk_in_id__in=[0, 1]).order_by('-vacancy_date')

#         closed_vacancies_data = []
#         for vacancy in closed_vacancies:
#             vacancy_data = {
#                 'id': vacancy.vacancy_id,
#                 'walk_in_id': vacancy.walk_in_id if vacancy.walk_in_id else "-",
#                 'branch_name': vacancy.branch if vacancy.branch else "-",
#                 'required_skills': vacancy.required_skills.split(",") if vacancy.required_skills else [],
#                 'job_role': vacancy.role if vacancy.role else "-",
#                 'no_of_vacancies': vacancy.capacity if vacancy.capacity else "-",
#                 'qualification_type': vacancy.qualification if vacancy.qualification else "-",
#                 'required_experience': vacancy.required_experience if vacancy.required_experience else "-",
#                 'salary': vacancy.salary if vacancy.salary else "-",
#                 'vacancy_date': vacancy.vacancy_date.strftime('%d-%m-%Y') if vacancy.vacancy_date else "-",
#             }
#             closed_vacancies_data.append(vacancy_data)

#         # Fetch walk-in vacancies
#         walk_in_vacancies = VacancyDetails.objects.filter(walk_in_id=1).order_by('-vacancy_date')

#         walk_in_vacancies_data = []
#         for vacancy in walk_in_vacancies:
#             vacancy_data = {
#                 'id': vacancy.vacancy_id,
#                 'walk_in_id': vacancy.walk_in_id if vacancy.walk_in_id else "-",
#                 'branch_name': vacancy.branch if vacancy.branch else "-",
#                 'required_skills': vacancy.required_skills.split(",") if vacancy.required_skills else [],
#                 'job_role': vacancy.role if vacancy.role else "-",
#                 'no_of_vacancies': vacancy.capacity if vacancy.capacity else "-",
#                 'qualification_type': vacancy.qualification if vacancy.qualification else "-",
#                 'required_experience': vacancy.required_experience if vacancy.required_experience else "-",
#                 'salary': vacancy.salary if vacancy.salary else "-",
#                 'vacancy_date': vacancy.vacancy_date.strftime('%d-%m-%Y') if vacancy.vacancy_date else "-",
#             }
#             walk_in_vacancies_data.append(vacancy_data)

#         response_data = {
#             'is_hr': is_hr,
#             'is_hrhead': is_hrhead,
#             'open_vacancies': open_vacancies_data,
#             'closed_vacancies': closed_vacancies_data,
#             'walk_in_vacancies': walk_in_vacancies_data,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

class VacancyListsAPIView(APIView):
    def get(self, request):
        is_hr = False
        is_hrhead = False
        response_data = {}

        # Check if the user is authenticated
        if request.user.is_authenticated:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = user_roll.roll_id == 1
                is_hrhead = user_roll.roll_id == 3
            except User_Rolls.DoesNotExist:
                pass

        today = datetime.today().date()

        # Fetch open vacancies
        open_vacancies = VacancyDetails.objects.filter(walk_in_id=0).order_by('-vacancy_date')

        # Serialize the queryset
        open_vacancies_data = VacancyDetailsSerializer(open_vacancies, many=True).data

        # Fetch closed vacancies
        closed_vacancies = VacancyDetails.objects.filter(walk_in_id__in=[0, 1]).order_by('-vacancy_date')

        # Serialize the queryset
        closed_vacancies_data = VacancyDetailsSerializer(closed_vacancies, many=True).data

        # Fetch walk-in vacancies
        walk_in_vacancies = VacancyDetails.objects.filter(walk_in_id=1).order_by('-vacancy_date')

        # Serialize the queryset
        walk_in_vacancies_data = VacancyDetailsSerializer(walk_in_vacancies, many=True).data

        response_data = {
            'is_hr': is_hr,
            'is_hrhead': is_hrhead,
            'open_vacancies': open_vacancies_data,
            'closed_vacancies': closed_vacancies_data,
            'walk_in_vacancies': walk_in_vacancies_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

# def candidate_vacancy_card_details(request,pk):
#     is_hr=False
#     is_hrhead = False
#     is_candidate = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#             is_candidate=True if user_roll.roll_id==0 else False
#         except:
#             pass
    
#     sql_query = f"""
#     SELECT * FROM "VACANCY_DETAILS" VD LEFT JOIN "INTERVIEW_DETAILS" ID ON VD.vacancy_id = ID.vacancy_id WHERE VD.vacancy_id={pk};
#                 """
#     vacancy_df = pd.read_sql_query(sql_query, engine)
#     # change the format of date to dd-mm-yyyy
#     vacancy_df['interview_date'] = vacancy_df['interview_date'].dt.strftime('%d-%m-%Y')

#     vacancy_df.fillna("-", inplace=True)
#     vacancy_obj = vacancy_df.to_dict("records")[0]  
#     return render(request,'candidate_vacancy_card_details.html',{'vacancy':vacancy_obj,'is_hr':is_hr ,'is_hrhead':is_hrhead,'is_candidate':is_candidate})

class CandidateVacancyCardDetailsAPIView(APIView):
    def get(self, request, pk):
        try:
            vacancy = VacancyDetails.objects.get(vacancy_id=pk)
            interview_details = InterviewDetails.objects.filter(vacancy_id=pk)
            
            # Serialize both VacancyDetails and InterviewDetails
            vacancy_serializer = VacancyDetailsSerializer(vacancy)
            interview_serializer = InterviewDetailsSerializer(interview_details, many=True)
            
            data = {
                'vacancy_details': vacancy_serializer.data,
                'interview_details': interview_serializer.data
            }
            return Response(data)
        except VacancyDetails.DoesNotExist:
            return Response({'error': 'Vacancy not found'}, status=404)
        

# def vacancy_card_details(request,pk):
#     is_hr=False
#     is_hrhead = False
#     is_candidate = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#             is_candidate=True if user_roll.roll_id==0 else False
#         except:
#             pass
    
#     sql_query = f"""
#     SELECT * FROM "VACANCY_DETAILS" VD LEFT JOIN "INTERVIEW_DETAILS" ID ON VD.vacancy_id = ID.vacancy_id WHERE VD.vacancy_id={pk};
#                 """
#     vacancy_df = pd.read_sql_query(sql_query, engine)
#     # change the format of date to dd-mm-yyyy
#     vacancy_df['interview_date'] = vacancy_df['interview_date'].dt.strftime('%d-%m-%Y')

#     vacancy_df.fillna("-", inplace=True)
#     vacancy_obj = vacancy_df.to_dict("records")[0]  
#     return render(request,'vacancy_card_details.html',{'vacancy':vacancy_obj,'is_hr':is_hr ,'is_hrhead':is_hrhead,'is_candidate':is_candidate})

class VacancyCardDetailsAPIView(APIView):
    def get(self, request, pk):
        try:
            # Fetch VacancyDetails and associated InterviewDetails for the given pk
            vacancy = VacancyDetails.objects.get(vacancy_id=pk)
            interview_details = InterviewDetails.objects.filter(vacancy_id=pk)

            # Serialize VacancyDetails and InterviewDetails
            vacancy_serializer = VacancyDetailsSerializer(vacancy)
            interview_serializer = InterviewDetailsSerializer(interview_details, many=True)

            # Construct the response data
            response_data = {
                'vacancy_details': vacancy_serializer.data,
                'interview_details': interview_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except VacancyDetails.DoesNotExist:
            # If VacancyDetails with the given pk does not exist, return 404 Not Found
            return Response({'error': 'Vacancy not found'}, status=status.HTTP_404_NOT_FOUND)

# def applied_vacancy_card_details(request,pk):
#     is_hr=False
#     is_hrhead = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#         except:
#             pass
#     user_id=request.user.id
#     email=request.user.email
#     user_roll=User_Rolls.objects.get(user_id=user_id)


#     candidate = candidate_details.objects.filter(email = request.user.email).values('id')
#     print('candidate',candidate)
#     int = InterviewDetails.objects.filter(vacancy_id = pk).values('interview_id')
#     print('interview_id',int)
#     # app = ApplicationDetails.objects.filter(interview_id__in = int,candidate_id__in = candidate)
#     # print('application_details',app.application_id)
#     df =pd.DataFrame(ApplicationDetails.objects.filter(interview_id__in = int,candidate_id__in = candidate).values()).to_dict(orient="records")
#     print(df)
#     print("df",df[0]['application_id'])
   
#     sql_query = f"""
#                 SELECT * FROM "VACANCY_DETAILS" VD LEFT JOIN "INTERVIEW_DETAILS" ID ON VD.vacancy_id = ID.vacancy_id LEFT JOIN "APPLICATION_DETAILS" AD
#                 ON ID.interview_id = AD.interview_id WHERE VD.vacancy_id={pk} and AD.application_id = {df[0]['application_id']};
#                 """
#     vacancy_df = pd.read_sql_query(sql_query, engine)

#     # change the format of date to dd-mm-yyyy
#     vacancy_df['interview_date'] = vacancy_df['interview_date'].dt.strftime('%d-%m-%Y')
#     vacancy_df.fillna("-", inplace=True)
#     vacancy_obj = vacancy_df.to_dict("records")[0]   
#     candidate = vacancy_df['candidate_id']
#     print('candidate', candidate)    
#     # interview = vacancy_df['interview_id'].astype(int)
#     # print('interview', interview)
    
#     application = ApplicationDetails.objects.filter(candidate_id=candidate).first()
#     return render(request,'applied_vacancy_card_details.html',{'is_hr':is_hr ,'is_hrhead':is_hrhead,'vacancy':vacancy_obj,'application':application,'status': application.application_status,'user_roll':user_roll,'email':email})

class AppliedVacancyCardDetailsAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            # Check if the user is authenticated
            if request.user.is_authenticated:
                # Retrieve candidate details based on user's email
                candidate = candidate_details.objects.get(email=request.user.email)
                # Retrieve application details for the candidate and vacancy
                application = ApplicationDetails.objects.get(candidate=candidate, vacancy_id=pk)
                # Retrieve vacancy details
                vacancy = VacancyDetails.objects.get(vacancy_id=pk)
                # Retrieve interview details
                interview = InterviewDetails.objects.get(vacancy_id=pk)
                
                # Serialize data
                application_serializer = ApplicationDetailsSerializer(application)
                vacancy_serializer = VacancyDetailsSerializer(vacancy)
                interview_serializer = InterviewDetailsSerializer(interview)
                
                # Return the serialized data
                return Response({
                    'application': application_serializer.data,
                    'vacancy': vacancy_serializer.data,
                    'interview': interview_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                # User is not authenticated
                return Response({'message': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        except candidate_details.DoesNotExist:
            # Candidate not found for the authenticated user
            return Response({'message': 'No candidate found for the authenticated user'}, status=status.HTTP_404_NOT_FOUND)
        except (ApplicationDetails.DoesNotExist, VacancyDetails.DoesNotExist, InterviewDetails.DoesNotExist):
            # Application, Vacancy, or Interview details not found
            return Response({'message': 'Details not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
# def sceduled_interview_details(request):
#     is_hr=False
#     is_hrhead = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#         except:
#             pass
#     context={}
#     #------
#     # extracts panel member user ids from panel_list column
#     def panel_id_extractor(request,interview_panel_list):
#         print("Type of interview panel list ",request.user.id,type(interview_panel_list))
#         print(interview_panel_list)
#         panel_id_list=[]
#         try:
#             # comma seperated ids in a string
#             panel_id_list=interview_panel_list.split(',')
#             panel_id_list_int = [int(x) for x in panel_id_list]
#             return panel_id_list_int
#         except Exception as e:
#             print('panel_id_extractor: ', str(e))
#             return panel_id_list

#     # checks if interviewer is in panel
#     def panel_checker(request,panel_id_list):
#         print(panel_id_list)
#         if request.user.id in panel_id_list:
#             return 1
#         else:
#             return 0

#     # current date
#     date = datetime.today().strftime('%Y-%m-%d')
#     # fetching applications whose interview has been scheduled
#     sql_query = f"""SET NOCOUNT ON;SELECT application_id,interview_id FROM application_details WHERE application_status = 5;SET NOCOUNT OFF"""
#     application_df=pd.read_sql_query(sql_query,engine)
#     application_df.dropna(inplace=True)
#     # list of interviews(ids) of those applications
#     interview_id_list = application_df['interview_id'].unique().tolist()
#     print(interview_id_list)
#     # secure interview instances of those applications
#     if application_df.empty:
#         return render(request, 'sceduled_Interview_Details.html',context)
#     if len(interview_id_list) == 1:
#         sql_query = f"""SET NOCOUNT ON;SELECT * FROM INTERVIEW_DETAILS WHERE interview_date = '{date}' and interview_id = {interview_id_list[0]};SET NOCOUNT OFF"""
#     else:
#         sql_query = f"""SET NOCOUNT ON;SELECT * FROM INTERVIEW_DETAILS WHERE interview_date = '{date}' and interview_id in {tuple(interview_id_list)};SET NOCOUNT OFF"""
#     interview_df=pd.read_sql_query(sql_query,engine)
#     print(interview_df.dtypes)
#     print(interview_df)

#     try:
#         #check in which panels he is present, first we find the panel member ids in each of the interviews
#         interview_df['panel_id_list'] = interview_df.apply(lambda x: panel_id_extractor(request,x['panel_list']), axis=1)
#         print(interview_df)
#         #then we check whether current interviewer is present in any of those panels
#         interview_df['panel_flag'] = interview_df.apply(lambda x: panel_checker(request,x['panel_id_list']), axis=1)
#         print(interview_df)
#         #interviews only where the current interviewer is present in the panel
#         interview_id_list = interview_df[interview_df['panel_flag']==1]['interview_id'].to_list()
#         print(interview_id_list)

#         # secure applications of these interviews(what the f)
#         if len(interview_id_list) == 0:
#             return render(request, 'sceduled_Interview_Details.html',context)
#         if len(interview_id_list) == 1:
#             sql_query = f"""SET NOCOUNT ON;SELECT * FROM application_details WHERE interview_id = {interview_id_list[0]} and application_status = 5;SET NOCOUNT OFF"""
#         else:
#             sql_query = f"""SET NOCOUNT ON;SELECT * FROM application_details WHERE interview_id in {tuple(interview_id_list)} and application_status = 5 ;SET NOCOUNT OFF"""
#         application_df=pd.read_sql_query(sql_query,engine)
#         sql_query = f"""SET NOCOUNT ON;SELECT * FROM candidate_details ;SET NOCOUNT OFF"""
#         candidate_df=pd.read_sql_query(sql_query,engine)
#         applicants=pd.merge(application_df,candidate_df,left_on='candidate_id',right_on='id',how='left')

#         context['applicants']=applicants.to_dict(orient='records')
#         print('dwaaaaaaa')
#         print(context['applicants'])
#         context['is_hr'] = is_hr
#         context['is_hrhead'] = is_hrhead
#         return render(request, 'sceduled_Interview_Details.html',context)
#     except Exception as e:
#         print('error', e)
#         return render(request, 'sceduled_Interview_Details.html',{'is_hr':is_hr ,'is_hrhead':is_hrhead})
from rest_framework.permissions import IsAuthenticated
class ScheduledInterviewDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        context = {}
        date = datetime.today().strftime('%Y-%m-%d')

        try:
            application_ids = ApplicationDetails.objects.filter(application_status=5).values_list('interview_id', flat=True)
            interview_details = InterviewDetails.objects.filter(interview_date=date, id__in=application_ids)

            serializer = InterviewDetailsSerializer(interview_details, many=True)
            serialized_interviews = serializer.data

            if serialized_interviews:
                application_details = ApplicationDetails.objects.filter(interview_id__in=[interview['id'] for interview in serialized_interviews])
                candidate_ids = application_details.values_list('candidate_id', flat=True)
                candidates = candidate_details.objects.filter(id__in=candidate_ids)

                application_serializer = ApplicationDetailsSerializer(application_details, many=True)
                candidate_serializer = CandidateDetailsSerializer(candidates, many=True)

                serialized_applications = application_serializer.data
                serialized_candidates = candidate_serializer.data

                for interview in serialized_interviews:
                    interview['applications'] = [app for app in serialized_applications if app['interview_id'] == interview['id']]
                    for application in interview['applications']:
                        application['candidate'] = next((candidate for candidate in serialized_candidates if candidate['id'] == application['candidate_id']), None)

                context['interviews'] = serialized_interviews

            context['is_hr'] = request.user.user_roll.roll_id == 1 if hasattr(request.user, 'user_roll') else False
            context['is_hrhead'] = request.user.user_roll.roll_id == 3 if hasattr(request.user, 'user_roll') else False

            return Response(context, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error:', e)
            return Response({"message": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def number_of_interviewer(request):
#     context={}
#     if request.method=='POST':
#         application_id=request.POST.get('application_id')
#         sql_query = f"""SET NOCOUNT ON;SELECT count(response_id) FROM interview_response WHERE application_id = {int(application_id)};SET NOCOUNT OFF"""
#         df=pd.read_sql_query(sql_query,engine)
#         print("DFFFFFFFFFFFFFFFFff")
#         print(df)
#         print(df.iat[0,0])
#         context['success']='success'
#         context['data_num']=int(df.iat[0,0])
#         if( df.iat[0,0] >= 3 ):
#             # user_details_obj=User_Details.objects.get(id=candidate_id)
#             user_details_obj=ApplicationDetails.objects.get(application_id=application_id)
#             user_details_obj.application_status='6'
#             user_details_obj.save()
#         return JsonResponse(context)

# class NumberOfInterviewerAPIView(APIView):
#     def post(self, request):
#         context = {}
#         application_id = request.data.get('application_id')

#         try:
#             response_count = InterviewResponse.objects.filter(application_id=application_id).count()
#             serializer = InterviewResponseSerializer(instance=response_count)
#             data = serializer.data

#             if response_count >= 3:
#                 application = ApplicationDetails.objects.get(application_id=application_id)
#                 application.application_status = '6'
#                 application.save()

#             context['success'] = 'success'
#             context['data'] = data
#             return JsonResponse(context)
#         except Exception as e:
#             print('Error:', e)
#             return JsonResponse({"message": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def offline_test_details(request):
#     is_hr=False
#     is_hrhead = False
#     if str(request.user) != 'AnonymousUser':
#         user_id=request.user.id
#         try:
#             user_roll=User_Rolls.objects.get(user_id=user_id)
#             is_hr=True if user_roll.roll_id==1 else False
#             is_hrhead=True if user_roll.roll_id==3 else False
#         except:
#             pass
#     query = """
#         SELECT 
#             cd.name, 
#             cd.email, 
#             cd.mobile_no, 
#             cd.id as candidate_id, 
#             ts.application_id
            
#         FROM test_schedule ts
#         LEFT JOIN candidate_details cd ON ts.candidate_id = cd.id 
#         WHERE ts.is_online = 0 and ts.test_status = 0
#     """
    
#     df = pd.read_sql(query, engine)
#     print(df, "data")
#     data_list = df.to_dict(orient='records')
#     print(data_list)
    
#     applicants= TestScheduleDetails.objects.filter(is_online = False).values_list('application_id', flat=True)
#     print("Applicants:", applicants)

#     candidate = candidate_details.objects.all()
    
#     generated_urls = []
#     for application_id in applicants:
#         url = reverse('update_test_score', kwargs={'refId': application_id})
#         generated_urls.append(url)

#     print("Generated URLs:", generated_urls)
    
    
#     context = {
#         'applicants': applicants,
#         'candidates': candidate,
#         'data_list': data_list,
#         'is_hr':is_hr ,'is_hrhead':is_hrhead,
#     }
    
#     return render(request, 'offline_test_details.html',context)

class OfflineTestDetailsAPIView(APIView):
    def get(self, request):
        is_hr = False
        is_hrhead = False
        
        if not request.user.is_anonymous:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = user_roll.roll_id == 1
                is_hrhead = user_roll.roll_id == 3
            except User_Rolls.DoesNotExist:
                pass
        
        queryset = TestScheduleDetails.objects.filter(is_online=False, test_status=0)
        serializer = TestScheduleDetailsSerializer(queryset, many=True)
        data = serializer.data
        
        context = {
            'applicants': data,
            'is_hr': is_hr,
            'is_hrhead': is_hrhead,
        }
        
        return Response(context)
    
class NumberOfInterviewerAPIView(APIView):
    def post(self, request):
        context = {}
        application_id = request.data.get('application_id')
        if application_id:
            try:
                num_interviewers = InterviewResponse.objects.filter(application_id=application_id).count()
                context['success'] = 'success'
                context['data_num'] = num_interviewers
                if num_interviewers >= 3:
                    application = ApplicationDetails.objects.get(application_id=application_id)
                    application.application_status = '6'
                    application.save()
                
                serializer = NumberOfInterviewerSerializer(data={'application_id': application_id, 'data_num': num_interviewers, 'success': 'success'})
                if serializer.is_valid():
                    return JsonResponse(serializer.data)
                else:
                    return JsonResponse(serializer.errors, status=400)
            except ApplicationDetails.DoesNotExist:
                return JsonResponse({'error': 'Application not found'}, status=404)
        else:
            return JsonResponse({'error': 'application_id is required'}, status=400)
        
class OnboardingCandidatesAPIView(APIView):
    def get(self, request):
        is_hr = False
        is_hrhead = False
        if not request.user.is_anonymous:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = user_roll.roll_id == 1
                is_hrhead = user_roll.roll_id == 3
            except User_Rolls.DoesNotExist:
                pass
        
        queryset = ApplicationDetails.objects.filter(application_status=7)
        serialized_data = []
        for application in queryset:
            candidate_id = application.candidate_id
            try:
                candidate = candidate_details.objects.get(id=candidate_id)
                serialized_data.append({
                    'name': candidate.name,
                    'email': candidate.email,
                    'mobile_no': candidate.mobile_no,
                    'candidate_id': candidate.id,
                    'application_id': application.application_id,
                    'position_shortlisted_for': application.position_shortlisted_for,
                    'branch_shortlisted_for': application.branch_shortlisted_for,
                })
            except candidate_details.DoesNotExist:
                pass
        
        context = {
            'applicants': serialized_data,
            'is_hr': is_hr,
            'is_hrhead': is_hrhead,
        }
        
        return Response(context)
    
class ShortlistCandidatesAPIView(APIView):
    def get(self, request):
        # Fetch the vacancy IDs associated with shortlisted applications
        application_statuses = [6]  # Assuming application status 6 represents shortlisted applications
        vacancy_ids = ApplicationDetails.objects.filter(application_status__in=application_statuses).values_list('branch_shortlisted_for', flat=True).distinct()

        # Query VacancyDetails based on retrieved vacancy IDs
        vacancies = VacancyDetails.objects.filter(branch__in=vacancy_ids)

        # Serialize the data
        serializer = VacancyDetailsSerializer(vacancies, many=True)

        return Response(serializer.data)

class AssessedCandidatesAPIView(APIView):
    def get(self, request, id=None):
        is_hr = False
        is_hrhead = False
        
        # Check if the user is authenticated
        if not request.user.is_anonymous:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = user_roll.roll_id == 1
                is_hrhead = user_roll.roll_id == 3
            except User_Rolls.DoesNotExist:
                pass
        
        # Retrieve assessed candidates' details
        try:
            applicants = ApplicationDetails.objects.filter(application_status=6, interview_id__isnull=False, interview_id=id)
            assessed_candidates = []
            for applicant in applicants:
                # Retrieve related interview details
                interview = InterviewDetails.objects.get(pk=applicant.interview_id)
                interview_serializer = InterviewDetailsSerializer(interview).data
                
                # Retrieve related candidate details
                candidate = candidate_details.objects.get(pk=applicant.candidate_id)
                candidate_serializer = CandidateDetailsSerializer(candidate).data
                
                # Retrieve related interview response details
                response = InterviewResponse.objects.filter(application_id=applicant.application_id).first()
                interview_score = response.score if response else None
                
                data = {
                    'candidate': candidate_serializer,
                    'application': ApplicationDetailsSerializer(applicant).data,
                    'interview': interview_serializer,
                    'interview_score': interview_score,
                }
                assessed_candidates.append(data)
            
            return Response({
                'is_hr': is_hr,
                'is_hrhead': is_hrhead,
                'assessed_candidates': assessed_candidates
            }, status=200)
        except Exception as e:
            return Response({'message': str(e)}, status=500)


from django.utils import timezone

# class RescheduleInterviewUserAPIView(APIView):
#     def get(self, request):
#         is_hr = False
#         is_hrhead = False
#         if not request.user.is_anonymous:
#             user_id = request.user.id
#             try:
#                 user_roll = User_Rolls.objects.get(user_id=user_id)
#                 is_hr = user_roll.roll_id == 1
#                 is_hrhead = user_roll.roll_id == 3
#             except User_Rolls.DoesNotExist:
#                 pass
        
#         # If user is not HR or HR Head, return error response
#         if not is_hr and not is_hrhead:
#             return Response({'message': 'User is not authorized to view this data'}, status=403)
        
#         # Fetch data using Django ORM
#         applicants = ApplicationDetails.objects.filter(
#             interview__interview_date__lt=datetime.now()
#         ).values('candidate__name', 'candidate__email', 'candidate__mobile_no', 'interview__interview_date')
        
#         # Serialize the data
#         serializer = RescheduleInterviewUserSerializer(applicants, many=True)
        
#         # Return the serialized data
#         return Response(serializer.data)
class RescheduleInterviewUserAPIView(APIView):
    def get(self, request):
        # Fetch data using Django ORM
        applicants = ApplicationDetails.objects.filter(
            interview_details__interview_date__lt=datetime.now()
        ).values('candidate__name', 'candidate__email', 'candidate__mobile_no', 'interview_details__interview_date')
        
        # Serialize the data
        serializer = RescheduleInterviewUserSerializer(applicants, many=True)
        
        # Return the serialized data
        return Response(serializer.data)
    

class ExamSnapshotDashboardAPIView(APIView):
    def get(self, request):
        is_hr = False
        is_hrhead = False
        if not request.user.is_anonymous:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = user_roll.roll_id == 1
                is_hrhead = user_roll.roll_id == 3
            except User_Rolls.DoesNotExist:
                pass

        test_schedules = TestScheduleDetails.objects.filter(is_online=True)
        candidate_ids = test_schedules.values_list('candidate_id', flat=True) 
        candidates = candidate_details.objects.filter(id__in = candidate_ids)

        test_schedule_serializer = TestScheduleDetailsSerializer(test_schedules, many=True)
        candidate_serializer = CandidateDetailsSerializer1(candidates, many=True)

        context = {
            'test_schedules': test_schedule_serializer.data,
            'candidates': candidate_serializer.data,
            'is_hr': is_hr,
            'is_hrhead': is_hrhead,
        }
        return Response(context)
    
class AllotedApplicationsAPIView(APIView):
    def get(self, request):
        is_hr = False
        is_hrhead = False
        if not request.user.is_anonymous:
            user_id = request.user.id
            try:
                user_roll = User_Rolls.objects.get(user_id=user_id)
                is_hr = user_roll.roll_id == 1
                is_hrhead = user_roll.roll_id == 3
            except User_Rolls.DoesNotExist:
                pass
            
        # Retrieve rejected applications data using Django ORM
        rejected_applications = RejectReviewAllotment.objects.filter(is_reviewed=False, alloted_to=request.user.id)
        
        # Serialize the data
        application_serializer = ApplicationDetailsSerializer(rejected_applications, many=True)
        allotment_serializer = RejectReviewAllotmentSerializer(rejected_applications, many=True)
        candidate_serializer = CandidateDetailsSerializer(rejected_applications.values('application_id'),many= True)

        return Response({
            'is_hr': is_hr,
            'is_hrhead': is_hrhead,
            'applications': application_serializer.data,
            'allotments': allotment_serializer.data,
            'candidates': candidate_serializer.data,
            'count': rejected_applications.count()
        })


class CandidateListAPIView(APIView):
    def get(self, request):
        application_status = request.GET.get('application_status', '7,11,12')  # Default value
        print('application_status', application_status)
        
        application_statuses = [int(status) for status in application_status.split(',')]
        candidates = candidate_details.objects.filter(application_details__application_status__in=application_statuses)
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)