from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import ProtectedError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .decorators import admin_required, captain_or_admin_required, student_or_above_required
from .forms import StudentForm, ClubForm, TeamForm, MembershipForm, FixtureForm
from .models import Student, SportsClub, Team, Membership, Fixture

@login_required
def dashboard(request):
    return render(request, 'sports/dashboard.html')

def placeholder(request, *args, **kwargs):
    return HttpResponse("Coming Soon....")

club_list = club_create = club_update = club_delete = placeholder
team_list = team_create = team_update = team_delete = placeholder
membership_list = membership_create = membership_update = membership_delete = placeholder
fixture_list = fixture_create = fixture_update = fixture_delete = placeholder
report_club_roster = report_team_fixtures = report_student_memberships = placeholder
club_detail = team_detail = student_detail = membership_detail = fixture_detail = placeholder 


@captain_or_admin_required
def student_list(request):
    students = Student.objects.all().order_by("last_name")
    return render(request, "sports/student_list.html", {"students": students})

@student_or_above_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.user.role == "student" and request.user.student_id != student.pk:
        raise PermissionDenied          # students may only view themselves
    return render(request, "sports/student_detail.html", {"student": student})

@admin_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Student added.")
        return redirect("student_list")
    return render(request, "sports/form.html", {"form": form, "title": "Add student"})

@admin_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, "Student updated.")
        return redirect("student_detail", pk=student.pk)
    return render(request, "sports/form.html", {"form": form, "title": "Edit student"})

@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        try:
            student.delete()
            messages.success(request, "Student deleted.")
        except ProtectedError:
            messages.error(request, "Can't delete: this student still has memberships.")
        return redirect("student_list")
    return render(request, "sports/confirm_delete.html",
                  {"object": student, "cancel_url": "student_list"})
# Create your views here.



def _safe_delete(request, obj, label, list_url):
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, f"{label} deleted.")
        except ProtectedError:
            messages.error(request, f"Can't delete this {label.lower()}: other records still depend on it.")
        return redirect(list_url)
    return render(request, "sports/confirm_delete.html",
                  {"object": obj, "cancel_url": list_url})

# ---------- CLUBS ----------
@student_or_above_required
def club_list(request):
    clubs = SportsClub.objects.all().order_by("club_name")
    return render(request, "sports/club_list.html", {"clubs": clubs})

@student_or_above_required
def club_detail(request, pk):
    club = get_object_or_404(SportsClub, pk=pk)
    return render(request, "sports/club_detail.html", {"club": club})

@admin_required
def club_create(request):
    form = ClubForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Club added.")
        return redirect("club_list")
    return render(request, "sports/form.html", {"form": form, "title": "Add club"})

@admin_required
def club_update(request, pk):
    club = get_object_or_404(SportsClub, pk=pk)
    form = ClubForm(request.POST or None, instance=club)
    if form.is_valid():
        form.save()
        messages.success(request, "Club updated.")
        return redirect("club_detail", pk=club.pk)
    return render(request, "sports/form.html", {"form": form, "title": "Edit club"})

@admin_required
def club_delete(request, pk):
    return _safe_delete(request, get_object_or_404(SportsClub, pk=pk), "Club", "club_list")


# ---------- TEAMS ----------
@student_or_above_required
def team_list(request):
    teams = Team.objects.select_related("club").order_by("club__club_name", "team_name")
    return render(request, "sports/team_list.html", {"teams": teams})

@student_or_above_required
def team_detail(request, pk):
    team = get_object_or_404(Team.objects.select_related("club"), pk=pk)
    return render(request, "sports/team_detail.html", {"team": team})

@admin_required
def team_create(request):
    form = TeamForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Team added.")
        return redirect("team_list")
    return render(request, "sports/form.html", {"form": form, "title": "Add team"})

@admin_required
def team_update(request, pk):
    team = get_object_or_404(Team, pk=pk)
    form = TeamForm(request.POST or None, instance=team)
    if form.is_valid():
        form.save()
        messages.success(request, "Team updated.")
        return redirect("team_detail", pk=team.pk)
    return render(request, "sports/form.html", {"form": form, "title": "Edit team"})

@admin_required
def team_delete(request, pk):
    return _safe_delete(request, get_object_or_404(Team, pk=pk), "Team", "team_list")


# ---------- MEMBERSHIPS ----------
@student_or_above_required
def membership_list(request):
    memberships = Membership.objects.select_related("student", "club", "team")
    if request.user.role == "student":          # students only see their own
        memberships = memberships.filter(student_id=request.user.student_id)
    return render(request, "sports/membership_list.html", {"memberships": memberships})

@student_or_above_required
def membership_detail(request, pk):
    m = get_object_or_404(Membership.objects.select_related("student", "club", "team"), pk=pk)
    if request.user.role == "student" and m.student_id != request.user.student_id:
        raise PermissionDenied
    return render(request, "sports/membership_detail.html", {"membership": m})

@admin_required
def membership_create(request):
    form = MembershipForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Membership added.")
        return redirect("membership_list")
    return render(request, "sports/form.html", {"form": form, "title": "Add membership"})

@admin_required
def membership_update(request, pk):
    m = get_object_or_404(Membership, pk=pk)
    form = MembershipForm(request.POST or None, instance=m)
    if form.is_valid():
        form.save()
        messages.success(request, "Membership updated.")
        return redirect("membership_detail", pk=m.pk)
    return render(request, "sports/form.html", {"form": form, "title": "Edit membership"})

@admin_required
def membership_delete(request, pk):
    return _safe_delete(request, get_object_or_404(Membership, pk=pk), "Membership", "membership_list")


# ---------- FIXTURES ----------
@student_or_above_required
def fixture_list(request):
    fixtures = Fixture.objects.select_related("home_team", "away_team").order_by("fixture_date", "start_time")
    return render(request, "sports/fixture_list.html", {"fixtures": fixtures})

@student_or_above_required
def fixture_detail(request, pk):
    f = get_object_or_404(Fixture.objects.select_related("home_team", "away_team"), pk=pk)
    return render(request, "sports/fixture_detail.html", {"fixture": f})

@admin_required
def fixture_create(request):
    form = FixtureForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Fixture scheduled.")
        return redirect("fixture_list")
    return render(request, "sports/form.html", {"form": form, "title": "Schedule fixture"})

@admin_required
def fixture_update(request, pk):
    f = get_object_or_404(Fixture, pk=pk)
    form = FixtureForm(request.POST or None, instance=f)
    if form.is_valid():
        form.save()
        messages.success(request, "Fixture updated.")
        return redirect("fixture_detail", pk=f.pk)
    return render(request, "sports/form.html", {"form": form, "title": "Edit fixture"})

@admin_required
def fixture_delete(request, pk):
    return _safe_delete(request, get_object_or_404(Fixture, pk=pk), "Fixture", "fixture_list")