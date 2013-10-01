from django import template
register = template.Library()

@register.filter
def name(person, user):
    """
    format the person's name according to permission
    """
    if person.profile.has_permission(user):
        return person.get_full_name()
    else:
        return "%s %s." % (person.first_name, person.last_name[0])

@register.filter
def fullname(person):
    return person.get_full_name()

@register.filter
def halfname(person):
    return "%s %s." % (person.first_name, person.last_name[0])
