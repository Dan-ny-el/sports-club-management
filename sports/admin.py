from django.contrib import admin
from .models import Student, SportsClub, Team, Membership, Fixture

admin.site.register([Student, SportsClub, Team, Membership, Fixture])