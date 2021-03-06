from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from base.util import with_author, with_timestamp
from competitions.models import Competition, Season
from events.models import EventUserRegistration


# User-related models
class UserProfile(models.Model):
    '''
    Represents an user profile. This contains non-auth information stored
    for the particular user.

    Any user can have both UserProfile and OrganizerProfile set.
    '''

    user = models.OneToOneField('auth.User',
                                verbose_name=_('user'))

    # personal info
    date_of_birth = models.DateField(blank=True,
                                     null=True,
                                     verbose_name=_('date of birth'))

    sex = models.CharField(max_length=1,
                           blank=True,
                           null=True,
                           choices=(('M', _('male')), ('F', _('female'))),
                           verbose_name=_('sex'))

    # address information
    phone_number = models.CharField(max_length=30,
                                    blank=True,
                                    null=True,
                                    verbose_name=_('phone number'))
    parent_phone_number = models.CharField(
                              max_length=30,
                              blank=True,
                              null=True,
                              verbose_name=_('parent phone number'))
    address = models.ForeignKey('schools.Address',
                                blank=True,
                                null=True,
                                verbose_name=_('address'))

    # school related info
    school = models.ForeignKey('schools.School',
                               blank=True,
                               null=True,
                               verbose_name=_('school'))
    school_class = models.CharField(max_length=20,
                                    blank=True,
                                    null=True,
                                    verbose_name=_('school class'))
    classlevel = models.CharField(max_length=2,
                                  blank=True,
                                  null=True,
                                  verbose_name=_('class level'),
                                  choices=(('Z2', 'Z2'),
                                           ('Z3', 'Z3'),
                                           ('Z4', 'Z4'),
                                           ('Z5', 'Z5'),
                                           ('Z6', 'Z6'),
                                           ('Z7', 'Z7'),
                                           ('Z8', 'Z8'),
                                           ('Z9', 'Z9'),
                                           ('S1', 'S1'),
                                           ('S2', 'S2'),
                                           ('S3', 'S3'),
                                           ('S4', 'S4')))

    # Fields added via foreign keys:

    #  camp_set
    #  campuserinvitation_set
    #  competitionuserregistration_set
    #  event_set
    #  eventuserregistration_set
    #  usersolution_set

    # Fields added via inheritance:

    #  organizer

    # Define autocomplete fields for grapelli search in admin
    @staticmethod
    def autocomplete_search_fields():
        return (
            'user__username__icontains',
            'user__first_name__icontains',
            'user__last_name__icontains',
        )

    def __unicode__(self):
        return unicode(_("user profile: {user}")
                       .format(user=self.user.username))

    @cached_property
    def organized_competitions(self):
        organized_competitions = (self.user.competitionorgregistration_set
                                  .filter(approved=True)
                                  .values('competition'))

        return Competition.objects.filter(id__in=organized_competitions)

    @cached_property
    def participated_competitions(self):
        season_competition = [s.competition.id
                              for s in self.participated_seasons]
        return Competition.objects.filter(id__in=season_competition)

    @cached_property
    def participated_seasons(self):
        participated_seasons = self.user.usersolution_set.values(
                               'problem__problemset__series__season')

        return list(Season.objects.filter(id__in=participated_seasons))

    def best_ranking(self):
        """
        Returns the competition, season and ranking when the user had the most
        success ever.
        """

        best_competition = None
        best_season = None
        best_ranking = None

        for season in self.participated_seasons:
            rank, _ = season.get_user_ranking(self.user)
            if rank < best_ranking or best_ranking is None:
                best_ranking = rank
                best_season = season
                best_competition = season.competition

        return best_competition, best_season, best_ranking

    def num_solved_problems(self):
        return self.user.usersolution_set.count()

    def num_attended_camps(self):
        return (EventUserRegistration.objects.filter(user=self.user)
                                             .exclude(event__camp=None)).count()

    def num_posted_comments(self):
        return self.user.comment_comments.count()

    def get_last_comments(self, number=10):
        return self.user.comment_comments.all()[:number]

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')


class OrganizerProfile(models.Model):
    '''
    Represents an organizer profile.

    Organizer can organize multiple competitions or events.
    '''

    user = models.OneToOneField('auth.User',
                                verbose_name=_('user'))
    motto = models.CharField(max_length=250,
                             blank=True,
                             null=True,
                             verbose_name=_('motto'))

    # TODO: there are 2 data descriptors added via many-to-many relationship
    #       in this case it's organized_event_set (custom name due to
    #       the fact that optional parameter related_name was defined)
    #       and eventorgregistration_set
    #       Investigate!

    # Fields added via foreign keys:

    #  competitionorgregistration_set
    #  eventorgregistration_set
    #  organized_event_set
    #  registeredorg
    #  orgsolution_set
    #  post_set

    # Fields added via inheritance:

    #  user_ptr

    # Define autocomplete fields for grapelli search in admin
    @staticmethod
    def autocomplete_search_fields():
        return (
            'organizer__username__icontains',
            'organizer__first_name__icontains',
            'organizer__last_name__icontains',
        )

    def __unicode__(self):
        return unicode(_("organizer profile: {user}")
                       .format(user=self.user.username))

    class Meta:
        verbose_name = _('organizer profile')
        verbose_name_plural = _('organizer profiles')


@receiver(post_save, sender=User)
def assign_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()


@with_author
@with_timestamp
class UserSeasonRegistration(models.Model):
    '''
    Represents a set of data in the profile that changes during
    the years and needs to be perserved in order to compute the
    results properly.
    '''

    user = models.ForeignKey('auth.User',
                             verbose_name=_('user'))

    season = models.ForeignKey('competitions.Season',
                               verbose_name=_('season'))

    school = models.ForeignKey('schools.School',
                               blank=True,
                               null=True,
                               verbose_name=_('school'))

    school_class = models.CharField(max_length=20,
                                    blank=True,
                                    null=True,
                                    verbose_name=_('school class'))

    classlevel = models.CharField(max_length=2,
                                  blank=True,
                                  null=True,
                                  verbose_name=_('class level'),
                                  choices=(('Z2', 'Z2'),
                                           ('Z3', 'Z3'),
                                           ('Z4', 'Z4'),
                                           ('Z5', 'Z5'),
                                           ('Z6', 'Z6'),
                                           ('Z7', 'Z7'),
                                           ('Z8', 'Z8'),
                                           ('Z9', 'Z9'),
                                           ('S1', 'S1'),
                                           ('S2', 'S2'),
                                           ('S3', 'S3'),
                                           ('S4', 'S4')))

    # Define autocomplete fields for grapelli search in admin
    @staticmethod
    def autocomplete_search_fields():
        return (
            'user__username__icontains',
            'user__first_name__icontains',
            'user__last_name__icontains',
        )

    @classmethod
    def register_user(cls, user, season):
        profile = user.userprofile

        registration = cls(
            user=user,
            season=season,
            school=profile.school,
            school_class=profile.school_class,
            classlevel=profile.classlevel,
            )

        registration.save()

    def __unicode__(self):
        return unicode(_("user registration for {season}: {user}")
                       .format(user=self.user.username,
                               season=self.season))

    class Meta:
        verbose_name = _('user season registration')
        verbose_name_plural = _('user season registrations')
        unique_together = ('season', 'user')
