# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from bbr3.admin import BbrAdmin
from people.models import Person, PersonAlias, ClassifiedPerson, PersonRelation


class PersonRelationAdmin(BbrAdmin):
    pass

class PersonAliasInline(admin.TabularInline):
    model = PersonAlias

class PersonAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("first_names", "surname")}
    inlines = [PersonAliasInline]
    search_fields = ['first_names', 'surname', 'suffix']
    
class ClassifiedPersonAdmin(BbrAdmin):
    list_filter = ('visible','show_on_homepage')
    list_display = ('__unicode__', 'owner', 'visible', 'show_on_homepage', 'created', 'last_modified')

admin.site.register(Person, PersonAdmin)
admin.site.register(PersonRelation, PersonRelationAdmin)
admin.site.register(ClassifiedPerson, ClassifiedPersonAdmin)
