from django import forms
from .models import Student
from django.db.models import Q
from .models import Student, SportsClub, Team, Membership, Fixture, User

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_id", "first_name", "last_name",
                  "contact_number", "age", "programme"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:                      # editing: ID can't change
            self.fields["student_id"].disabled = True

    def clean_age(self):
        age = self.cleaned_data["age"]
        if not 16 <= age <= 80:
            raise forms.ValidationError("Age must be between 16 and 80.")
        return age

    def clean_contact_number(self):
        number = self.cleaned_data["contact_number"]
        if not number.replace("-", "").replace(" ", "").isdigit():
            raise forms.ValidationError("Contact number must contain digits only.")
        return number


    from datetime import date as _date

class ClubForm(forms.ModelForm):
    class Meta:
        model = SportsClub
        fields = ["club_name", "sport_type", "date_created", "status", "manager"]
        widgets = {"date_created": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["manager"].queryset = User.objects.filter(role__in=["admin", "captain"])

    def clean_date_created(self):
        d = self.cleaned_data["date_created"]
        if d > _date.today():
            raise forms.ValidationError("Date created cannot be in the future.")
        return d


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["team_name", "club", "coach_name", "status"]


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["student", "club", "team", "registration_date", "payment_date",
                  "fee_amount", "payment_status", "membership_status"]
        widgets = {
            "registration_date": forms.DateInput(attrs={"type": "date"}),
            "payment_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_fee_amount(self):
        fee = self.cleaned_data["fee_amount"]
        if fee <= 0:
            raise forms.ValidationError("Fee must be greater than zero.")
        return fee

    def clean(self):
        cleaned = super().clean()
        club, team = cleaned.get("club"), cleaned.get("team")
        status, paid_on = cleaned.get("payment_status"), cleaned.get("payment_date")
        if team and club and team.club_id != club.pk:
            self.add_error("team", "This team does not belong to the selected club.")
        if status == "paid" and not paid_on:
            self.add_error("payment_date", "Enter the payment date for a paid membership.")
        if status != "paid" and paid_on:
            self.add_error("payment_status", "A payment date was entered, so mark it as paid.")
        return cleaned


class FixtureForm(forms.ModelForm):
    class Meta:
        model = Fixture
        fields = ["fixture_date", "start_time", "end_time", "venue",
                  "home_team", "away_team", "home_score", "away_score", "match_status"]
        widgets = {
            "fixture_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned = super().clean()
        home, away = cleaned.get("home_team"), cleaned.get("away_team")
        day = cleaned.get("fixture_date")
        start, end = cleaned.get("start_time"), cleaned.get("end_time")
        status = cleaned.get("match_status")

        if home and away and home == away:
            raise forms.ValidationError("Home and away team must be different.")
        if start and end and end <= start:
            self.add_error("end_time", "End time must be after the start time.")

        # Clash check: a team can't have two live fixtures on the same date
        if home and away and day:
            others = (Fixture.objects.filter(fixture_date=day)
                      .exclude(pk=self.instance.pk)
                      .exclude(match_status__in=["cancelled", "postponed"]))
            for team in (home, away):
                if others.filter(Q(home_team=team) | Q(away_team=team)).exists():
                    raise forms.ValidationError(
                        f"{team.team_name} already has a fixture on {day}.")

        if status == "completed" and (cleaned.get("home_score") is None
                                      or cleaned.get("away_score") is None):
            raise forms.ValidationError("Enter both scores for a completed fixture.")
        return cleaned