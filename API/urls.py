from . import views
from django.urls import path
from API.views import LoginAPIView, LogoutAPIView, SignInAPIView,AllotedApplicationsAPIView, AppliedVacancyCardDetailsAPIView, AssessedCandidatesAPIView, CandidateListAPIView,  CandidateVacancyCardDetailsAPIView, ExamSnapshotDashboardAPIView, NumberOfInterviewerAPIView, OfflineTestDetailsAPIView, OnboardingCandidatesAPIView, RescheduleInterviewUserAPIView, ScheduleOnlineTestAPIView, ScheduledInterviewDetailsAPIView,ScheduledUserDetailsAPIView,HoldUserDetailsAPIView, ShortlistCandidatesAPIView, SignUpAPIView, VacancyCardDetailsAPIView,VacancyListsAPIView


urlpatterns = [
    path('LoginAPIView/', LoginAPIView.as_view(), name='LoginAPIView'),
    path('SignInAPIView/', SignInAPIView.as_view(), name='SignInAPIView'),
    path('LogoutAPIView/', LogoutAPIView.as_view(), name='LogoutAPIView'),
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('ScheduleOnlineTestAPIView/', ScheduleOnlineTestAPIView.as_view(), name='ScheduleOnlineTestAPIView'),
    path('ScheduledUserDetailsAPIView/', ScheduledUserDetailsAPIView.as_view(), name='ScheduledUserDetailsAPIView'),
    path('HoldUserDetailsAPIView/', HoldUserDetailsAPIView.as_view(), name='HoldUserDetailsAPIView'),
    path('VacancyListsAPIView/', VacancyListsAPIView.as_view(), name='VacancyListsAPIView'),
    path('CandidateVacancyCardDetailsAPIView/<int:pk>/', CandidateVacancyCardDetailsAPIView.as_view(), name='CandidateVacancyCardDetailsAPIView'),
    path('VacancyCardDetailsAPIView/<int:pk>/', VacancyCardDetailsAPIView.as_view(), name='VacancyCardDetailsAPIView'),
    path('AppliedVacancyCardDetailsAPIView/<int:pk>/', AppliedVacancyCardDetailsAPIView.as_view(), name='AppliedVacancyCardDetailsAPIView'),
    path('ScheduledInterviewDetailsAPIView/', ScheduledInterviewDetailsAPIView.as_view(), name='ScheduledInterviewDetailsAPIView'),
    path('NumberOfInterviewerAPIView/', NumberOfInterviewerAPIView.as_view(), name='NumberOfInterviewerAPIView'),
    path('OfflineTestDetailsAPIView/', OfflineTestDetailsAPIView.as_view(), name='OfflineTestDetailsAPIView'),
    path('OnboardingCandidatesAPIView/', OnboardingCandidatesAPIView.as_view(), name='OnboardingCandidatesAPIView'),
    path('ShortlistCandidatesAPIView/', ShortlistCandidatesAPIView.as_view(), name='ShortlistCandidatesAPIView'),
    path('AssessedCandidatesAPIView/<int:id>/', AssessedCandidatesAPIView.as_view(), name='AssessedCandidatesAPIView'),
    path('RescheduleInterviewUserAPIView/', RescheduleInterviewUserAPIView.as_view(), name='RescheduleInterviewUserAPIView'),
    path('AllotedApplicationsAPIView/', AllotedApplicationsAPIView.as_view(), name='AllotedApplicationsAPIView'),
    path('CandidateListAPIView/', CandidateListAPIView.as_view(), name='CandidateListAPIView'),
    path('ExamSnapshotDashboardAPIView/', ExamSnapshotDashboardAPIView.as_view(), name='ExamSnapshotDashboardAPIView'),
    path('ScheduleOnlineTest/', views.ScheduleOnlineTest, name='ScheduleOnlineTest'),

]