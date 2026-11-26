from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.db import models
from django.db.models import F, Q


# ---------------------------------------------------------------------------
# Users (system accounts: admin, club manager, coach, etc.)
# ---------------------------------------------------------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), full_name=full_name, **extra)
        user.set_password(password)  # stored hashed in password_hash column
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra):
        extra.setdefault("role", "admin")
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, full_name, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Club Manager"),
        ("coach", "Coach"),
        ("student", "Student"),
    ]
    ACCOUNT_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("suspended", "Suspended"),
    ]

    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)
    # Overrides AbstractBaseUser.password so the column is called password_hash
    password = models.CharField("password_hash", max_length=128, db_column="password_hash")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    account_status = models.CharField(
        max_length=20, choices=ACCOUNT_STATUS_CHOICES, default="active"
    )
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=64, blank=True, null=True)

    # Needed by Django admin / auth
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"

    @property
    def is_active(self):
        return self.account_status == "active"

    def __str__(self):
        return f"{self.full_name} ({self.role})"


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------
class Student(models.Model):
    student_id = models.CharField(max_length=20, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=20)
    age = models.PositiveSmallIntegerField()
    programme = models.CharField(max_length=100)

    class Meta:
        db_table = "student"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"


# ---------------------------------------------------------------------------
# Sports Club   (User --Manages--> Sports Club)
# ---------------------------------------------------------------------------
class SportsClub(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    club_id = models.AutoField(primary_key=True)
    club_name = models.CharField(max_length=100, unique=True)
    sport_type = models.CharField(max_length=50)
    date_created = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="manager_id",
        related_name="managed_clubs",
    )

    class Meta:
        db_table = "sports_club"

    def __str__(self):
        return self.club_name


# ---------------------------------------------------------------------------
# Team   (Club has Teams)
# ---------------------------------------------------------------------------
class Team(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100)
    club = models.ForeignKey(
        SportsClub,
        on_delete=models.PROTECT,
        db_column="club_id",
        related_name="teams",
    )
    coach_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        db_table = "team"
        constraints = [
            models.UniqueConstraint(fields=["club", "team_name"], name="uniq_team_name_per_club"),
        ]

    def __str__(self):
        return self.team_name


# ---------------------------------------------------------------------------
# Membership
#   Student --Registers--> Membership
#   Membership --Belongs To--> Sports Club
#   Team --Has members--> Membership
# ---------------------------------------------------------------------------
class Membership(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("overdue", "Overdue"),
    ]
    MEMBERSHIP_STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("expired", "Expired"),
    ]

    membership_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        db_column="student_id",
        related_name="memberships",
    )
    club = models.ForeignKey(
        SportsClub,
        on_delete=models.PROTECT,
        db_column="club_id",
        related_name="memberships",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="team_id",
        related_name="memberships",
    )
    registration_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    membership_status = models.CharField(
        max_length=20, choices=MEMBERSHIP_STATUS_CHOICES, default="active"
    )

    class Meta:
        db_table = "membership"
        constraints = [
            models.UniqueConstraint(fields=["student", "club"], name="uniq_student_club"),
        ]

    def __str__(self):
        return f"{self.student_id} -> {self.club_id}"


# ---------------------------------------------------------------------------
# Fixtures / Matches
#   Team --Plays as home team in--> Fixture
#   Team --Plays as away team in--> Fixture
# ---------------------------------------------------------------------------
class Fixture(models.Model):
    MATCH_STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("postponed", "Postponed"),
        ("cancelled", "Cancelled"),
    ]

    fixture_id = models.AutoField(primary_key=True)
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column="home_team_id",
        related_name="home_fixtures",
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        db_column="away_team_id",
        related_name="away_fixtures",
    )
    fixture_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=150)
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    match_status = models.CharField(
        max_length=20, choices=MATCH_STATUS_CHOICES, default="scheduled"
    )

    class Meta:
        db_table = "fixtures_matches"
        constraints = [
            models.CheckConstraint(
                check=~Q(home_team=F("away_team")),
                name="home_team_not_equal_away_team",
            ),
        ]

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.fixture_date})"
