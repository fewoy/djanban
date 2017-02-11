# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

import math

import numpy
from django.contrib.auth.models import User
from django.db import models
from django.db import transaction
from django.db.models import Sum, Avg, Q
from django.utils import timezone
from isoweek import Week

from djangotrellostats.apps.base.auth import get_user_boards


class Member(models.Model):
    DEFAULT_MAX_NUMBER_OF_BOARDS = 2

    creator = models.ForeignKey("members.Member", related_name="created_members", null=True, default=None, blank=True)

    user = models.OneToOneField(User, verbose_name=u"Associated user", related_name="member", null=True, default=None)

    biography = models.TextField(verbose_name=u"Biography", blank=True, default="")

    is_developer = models.BooleanField(verbose_name=u"Is this member a developer?",
                                       help_text=u"Informs if this member is a developer and hence will receive reports"
                                                 u" and other information", default=False)

    on_holidays = models.BooleanField(verbose_name=u"Is this developer on holidays?",
                                      help_text=u"If the developer is on holidays will stop receiving reports "
                                                u"and other emails", default=False)

    minimum_working_hours_per_day = models.PositiveIntegerField(
        verbose_name=u"Minimum number hours this developer should complete each day",
        default=None, null=True, blank=True)

    minimum_working_hours_per_week = models.PositiveIntegerField(
        verbose_name=u"Minimum number of hours this developer should complete per week",
        default=None, null=True, blank=True)

    spent_time_factor = models.DecimalField(
        decimal_places=2, max_digits=5,
        verbose_name=u"Factor that needs to be multiplied on the spent time price for this member",
        help_text=u"Modify this value whe this member cost8needs to be adjusted by a factor",
        default=1
    )

    max_number_of_boards = models.PositiveIntegerField(
        verbose_name=u"Max number of boards",
        help_text=u"Maximum number of boards this member can fetch. If null, unlimited number of boards",
        default=None, null=True
    )

    is_public = models.BooleanField(verbose_name=u"Check this if you want other members to add you to their boards",
                                    default=False, blank=True)

    # Constructor for Member
    def __init__(self, *args, **kwargs):
        super(Member, self).__init__(*args, **kwargs)

    # A native member is one that has no Trello profile
    @property
    def is_native(self):
        return not self.has_trello_profile

    # Inform if this member was fetched from Trello (alias method).
    @property
    def has_trello_profile(self):
        return hasattr(self, "trello_member_profile") and self.trello_member_profile

    # Inform if this member was fetched from Trello
    @property
    def has_trello_member_profile(self):
        return self.has_trello_profile

    # Has this uses credentials to make actions with the Trello API?
    @property
    def has_trello_credentials(self):
        return self.has_trello_profile and self.trello_member_profile.is_initialized

    @property
    def uuid(self):
        if self.has_trello_profile:
            return self.trello_member_profile.trello_id
        return self.id

    # Alias very useful for now
    @property
    def external_username(self):
        if self.has_trello_profile:
            return self.trello_member_profile.username
        if self.user:
            return self.user.username
        return "Member {0}".format(self.id)

    @property
    def initials(self):
        if self.has_trello_profile:
            return self.trello_member_profile.initials
        if self.user:
            return self.user.username
        return "Member {0}".format(self.id)

    # Return the members this member can see. That is:
    # - Members of one of his/her boards.
    # - Members created by this member.
    # - Public members.
    @property
    def viewable_members(self):
        boards = []
        if self.user:
            boards = get_user_boards(self.user)
        return Member.objects.filter(Q(boards__in=boards) | Q(creator=self) | Q(is_public=True)).distinct()

    @property
    def team_mates(self):
        boards = get_user_boards(self.user)
        return Member.objects.filter(boards__in=boards).distinct().order_by("name")

    # Get members that work with this user
    @staticmethod
    def get_user_team_mates(user):
        boards = get_user_boards(user)
        return Member.objects.filter(boards__in=boards).distinct().order_by("name")

    # Resets the password of the associated user of this member
    def reset_password(self, new_password=None):
        # A member without an user cannot be his/her password changed
        if not self.user:
            raise ValueError(u"This member has not an associated user")
        # Create automatically a new password if None is passed
        if new_password is None:
            new_password = User.objects.make_random_password()
        # Setting up the new password
        self.user.set_password(new_password)
        self.user.save()
        return new_password

    # Returns cards that belongs to this member and are currently under development
    def get_current_development_cards(self, board=None):
        development_cards = self.cards.filter(is_closed=False, list__type="development")
        # Filtering development cards by board
        if board:
            return development_cards.filter(board=board)
        return development_cards

    # Returns cards that are in development ordered by descending order according to when were worked on.
    def get_last_development_cards(self, board=None):
        development_cards = self.get_current_development_cards(board=board)
        return development_cards.order_by("-last_activity_datetime")

    # Returns the number of hours this member has develop today
    def get_today_spent_time(self, board=None):
        # Note that only if the member is a developer can his/her spent time computed
        if not self.is_developer:
            raise AssertionError(u"This member is not a developer")
        # We assume that we will not be working on holidays ever
        if self.on_holidays:
            return 0
        # Getting the spent time for today
        now = timezone.now()
        today = now.date()
        return self.get_spent_time(today, board)

    # Returns the number of hours this member developed yesterday
    def get_yesterday_spent_time(self, board=None):
        now = timezone.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        return self.get_spent_time(yesterday, board)

    # Returns the number of hours this member has develop on a given date
    def get_spent_time(self, date, board=None):
        # Note that only if the member is a developer can his/her spent time computed
        if not self.is_developer:
            raise AssertionError(u"This member is not a developer")

        spent_time_on_date_filter = {"date": date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_date_filter["board"] = board

        return self._get_spent_time_sum_from_filter(spent_time_on_date_filter)

    # Returns the number of hours this member has develop on a given week
    def get_weekly_spent_time(self, week, year, board=None):
        start_date = Week(year, week).monday()
        end_date = Week(year, week).friday()
        spent_time_on_week_filter = {"date__gte": start_date, "date__lte": end_date}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_week_filter["board"] = board

        return self._get_spent_time_sum_from_filter(spent_time_on_week_filter)

    # Returns the number of hours this member has develop on a given month
    def get_monthly_spent_time(self, month, year, board=None):
        spent_time_on_week_filter = {"date__month": month, "date__year": year}

        # If we pass the board, only this board spent times will be given
        if board is not None:
            spent_time_on_week_filter["board"] = board

        return self._get_spent_time_sum_from_filter(spent_time_on_week_filter)

    # Returns the number of hours this member has develop given a filter
    def _get_spent_time_sum_from_filter(self, spent_time_filter):
        spent_time_on_date = self.daily_spent_times.filter(**spent_time_filter). \
            aggregate(sum=Sum("spent_time"))["sum"]

        if spent_time_on_date is None:
            return 0
        return spent_time_on_date

    # Destroy boards created by this member
    def delete_current_data(self):
        self.created_boards.all().delete()

    # Mood of this member
    @property
    def mood(self):
        happy_days = self.daily_member_moods.filter(mood="happy").count()
        normal_days = self.daily_member_moods.filter(mood="normal").count()
        sad_days = self.daily_member_moods.filter(mood="sad").count()
        all_days = (happy_days + normal_days + sad_days)
        if all_days == 0:
            return 0.0
        return 1.0 * (happy_days - sad_days) / all_days

    def get_role(self, board):
        try:
            return self.roles.get(board=board)
        except MemberRole.DoesNotExist:
            member_role, created = MemberRole.objects.get_or_create(type="normal", board=board)
            member_role.members.add(self)
        return member_role

    @property
    def active_cards(self):
        return self.cards.filter(is_closed=False).order_by("position")

    @property
    def number_of_cards(self):
        return self.active_cards.count()

    @property
    def forward_movements(self):
        return self.card_movements.filter(type="forward").count()

    @property
    def backward_movements(self):
        return self.card_movements.filter(type="backward").count()

    def get_forward_movements_for_board(self, board):
        return self.card_movements.filter(type="forward", board=board).count()

    def get_backward_movements_for_board(self, board):
        return self.card_movements.filter(type="backward", board=board).count()

    # Average lead time of the cards of this member
    @property
    def avg_card_lead_time(self):
        return self.active_cards.aggregate(avg=Avg("lead_time"))["avg"]

    # Average spent time of the cards of this member
    @property
    def avg_card_spent_time(self):
        return self.active_cards.aggregate(avg=Avg("spent_time"))["avg"]

    # Average estimated time of the cards of this member
    @property
    def avg_card_estimated_time(self):
        return self.active_cards.aggregate(avg=Avg("estimated_time"))["avg"]

    # Standard deviation of the lead time of the cards of this member
    @property
    def std_dev_card_lead_time(self):
        values = [float(card_i.lead_time) for card_i in self.active_cards.exclude(lead_time=None)]
        std_dev_time = numpy.nanstd(values)
        return std_dev_time

    # Standard deviation of the spent time of the cards of this member
    @property
    def std_dev_card_spent_time(self):
        values = [float(card_i.spent_time) for card_i in self.active_cards.exclude(spent_time=None)]
        std_dev_time = numpy.nanstd(values)
        return std_dev_time

    # Standard deviation of the estimated time of the cards of this member
    @property
    def std_dev_card_estimated_time(self):
        values = [float(card_i.estimated_time) for card_i in self.active_cards.exclude(estimated_time=None)]
        std_dev_time = numpy.nanstd(values)
        return std_dev_time


# Role a member has in a board
class MemberRole(models.Model):
    TYPE_CHOICES = (
        ("admin", "Administrator"),
        ("normal", "Normal"),
        ("guest", "Guest")
    )
    type = models.CharField(verbose_name="Role a member has in a board", default="normal", max_length=32)
    members = models.ManyToManyField("members.Member", verbose_name=u"Member", related_name="roles")
    board = models.ForeignKey("boards.Board", verbose_name=u"Boards", related_name="roles")

    # Return the full name of the type
    @property
    def name(self):
        return dict(MemberRole.TYPE_CHOICES)[self.type]


#
class TrelloMemberProfile(models.Model):

    api_key = models.CharField(max_length=128, verbose_name=u"Trello API key", null=True, default=None, blank=True)

    api_secret = models.CharField(max_length=128, verbose_name=u"Trello API secret", null=True, default=None, blank=True)

    token = models.CharField(max_length=128, verbose_name=u"Trello token", null=True, default=None, blank=True)

    token_secret = models.CharField(max_length=128, verbose_name=u"Trello token secret", null=True, default=None, blank=True)

    trello_id = models.CharField(max_length=128, verbose_name=u"Trello member id", unique=True)

    username = models.CharField(max_length=128, verbose_name=u"Trello username")

    initials = models.CharField(max_length=8, verbose_name=u"User initials in Trello")

    member = models.OneToOneField(Member, verbose_name=u"Associated member", related_name="trello_member_profile", null=True, default=None)

    # Informs if this member is initialized, that is, it has the credentials needed for connecting to trello.com
    @property
    def is_initialized(self):
        return self.api_key and self.api_secret and self.token and self.token_secret

    @property
    def user(self):
        if self.member:
            return self.member.user
        return None