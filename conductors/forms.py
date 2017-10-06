# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.forms import ModelForm

from conductors.models import Conductor


class EditConductorForm(ModelForm):
    """
    Form for entering a new conductor
    """
    class Meta:
        model = Conductor
        fields = ('first_names', 'surname', 'suffix')
        
class EditConductorAsSuperuserForm(ModelForm):
    """
    Form for entering a new conductor as a superuser
    """
    class Meta:
        model = Conductor
        fields = ('first_names','surname','suffix', 'bandname','start_date','end_date')