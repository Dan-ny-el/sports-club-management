from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'sports/dashboard.html')

def placeholder(request, *args, **kwargs):
    return HttpResponse("Coming Soon....")

club_list = club_create = club_update = club_delete = placeholder
team_list = team_create = team_update = team_delete = placeholder
student_list = student_create = student_update = student_delete = placeholder
membership_list = membership_create = membership_update = membership_delete = placeholder
fixture_list = fixture_create = fixture_update = fixture_delete = placeholder
report_club_roster = report_team_fixtures = report_student_memberships = placeholder
club_detail = team_detail = student_detail = membership_detail = fixture_detail = placeholder 

# Create your views here.
