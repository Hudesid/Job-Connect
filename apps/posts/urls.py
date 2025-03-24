from django.urls import path
from . import views


urlpatterns = [
    path("job-postings/list/", views.JobPostingListAPIView.as_view(), name="job_posting_list"),
    path("job-postings/announce/", views.JobPostingCreateAPIView.as_view(), name="job_posting_announce"),
    path("job-postings/detail/<int:pk>/", views.JobPostingRetrieveAPIView.as_view(), name="job_posting_detail"),
    path("job-postings/my-post/<int:pk>/", views.JobPostingRetrieveUpdateDestroyAPIView.as_view(), name="my_post_detail"),
    path("job-postings/recommended/", views.JobPostingRecommendedListAPIView.as_view(), name="job_posting_recommended"),
    path("applications/", views.JobApplicationListCreateAPIView.as_view(), name="my_applications"),
    path("applications/detail/<int:pk>/", views.JobApplicationRetrieveAPIView.as_view(), name="application_detail"),
    path("applications/<int:pk>/status/", views.JobApplicationUpdateAPIView.as_view(), name="application_update_status"),
    path("job-postings/<int:pk>/applications/", views.JobPostingApplicationListAPIView.as_view(), name="applications_of_job_postings"),
    path("applications/my-application/<int:pk>/", views.JobApplicationRetrieveUpdateDestroyAPIView.as_view(), name="my_application_detail"),
    path("saved-jobs/", views.SavedJobListAPIView.as_view(), name="saved_jobs"),
    path("saved-jobs/delete/<int:pk>/", views.SavedJobDestroyAPIView.as_view(), name="saved_jobs_update"),
    path("stats/job-postings/", views.JobPostingStatsListAPIView.as_view(), name="job_postings_stats"),
    path("stats/applications/", views.JobApplicationStatsListAPIView.as_view(), name="job_applications_stats")
]