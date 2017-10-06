# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.db import models

from bands.models import Band
from contests.models import ContestEvent
from people.models import Person


class ResultObject(object):
    pass


class ContestAdjudicator(models.Model):
    """
    A link between an adjudicator and a contest
    """ 
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest_event = models.ForeignKey(ContestEvent)
    person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=True, null=True)
    adjudicator_name = models.CharField(max_length=100,blank=True,null=True, help_text="Original adjudicator name entered")
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='ContestAdjudicatorLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='ContestAdjudicatorOwner')
    
        
    def __unicode__(self):
        return "%s %s" % (self.contest_event.name, self.person.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestAdjudicator, self).save()
    
    class Meta:
        ordering = ['contest_event']     