from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="sports/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Clubs
    path("clubs/", views.club_list, name="club_list"),
    path("clubs/add/", views.club_create, name="club_create"),
    path("clubs/<int:pk>/", views.club_detail, name="club_detail"),
    path("clubs/<int:pk>/edit/", views.club_update, name="club_update"),
    path("clubs/<int:pk>/delete/", views.club_delete, name="club_delete"),

    # Teams
    path("teams/", views.team_list, name="team_list"),
    path("teams/add/", views.team_create, name="team_create"),
    path("teams/<int:pk>/", views.team_detail, name="team_detail"),
    path("teams/<int:pk>/edit/", views.team_update, name="team_update"),
    path("teams/<int:pk>/delete/", views.team_delete, name="team_delete"),

    # Students (primary key is a string, student_id)
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_create, name="student_create"),
    path("students/<str:pk>/", views.student_detail, name="student_detail"),
    path("students/<str:pk>/edit/", views.student_update, name="student_update"),
    path("students/<str:pk>/delete/", views.student_delete, name="student_delete"),

    # Memberships
    path("memberships/", views.membership_list, name="membership_list"),
    path("memberships/add/", views.membership_create, name="membership_create"),
    path("memberships/<int:pk>/", views.membership_detail, name="membership_detail"),
    path("memberships/<int:pk>/edit/", views.membership_update, name="membership_update"),
    path("memberships/<int:pk>/delete/", views.membership_delete, name="membership_delete"),

    # Fixtures
    path("fixtures/", views.fixture_list, name="fixture_list"),
    path("fixtures/add/", views.fixture_create, name="fixture_create"),
    path("fixtures/<int:pk>/", views.fixture_detail, name="fixture_detail"),
    path("fixtures/<int:pk>/edit/", views.fixture_update, name="fixture_update"),
    path("fixtures/<int:pk>/delete/", views.fixture_delete, name="fixture_delete"),

    # Reports
    path("reports/club-roster/", views.report_club_roster, name="report_club_roster"),
    path("reports/team-fixtures/", views.report_team_fixtures, name="report_team_fixtures"),
    path("reports/student-memberships/", views.report_student_memberships, name="report_student_memberships"),
]

