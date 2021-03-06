from django.db import models
from django.utils.translation import ugettext as _
from base.util import with_author, with_timestamp

@with_author
@with_timestamp
class News(models.Model):
    """
    Represents a short information message.
    """

    competition = models.ForeignKey('competitions.Competition',
                                    verbose_name=_('competition'))
    heading = models.CharField(max_length=500,
                               verbose_name=_('heading'))
    text = models.CharField(max_length=500,
                            verbose_name=_('text'),
                            null=True,
                            blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("competition__name__icontains", "heading__icontains")

    def __unicode__(self):
        return self.heading

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
