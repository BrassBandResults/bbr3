# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from adjudicators.models import Adjudicator
from django.forms import ModelForm

class EditAdjudicatorForm(ModelForm):
    """
    Form for editing a new adjudicator
    """
    class Meta:
        model = Adjudicator
        fields = ('email','first_names','surname','suffix','deceased')