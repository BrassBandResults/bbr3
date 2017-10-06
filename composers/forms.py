# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.forms import ModelForm

from pieces.models import Composer


class EditComposerForm(ModelForm):
    """
    Form for entering a new composer
    """
    class Meta:
        model = Composer
        fields = ('first_names','surname', 'suffix')