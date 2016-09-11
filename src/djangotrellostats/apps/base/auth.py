
from django.conf import settings


def member_is_administrator(member):
    """
    Check if the member is an administrator of this platform.
    Parameters
    ----------
    member: member.Member to be checked.

    Returns
    -------
    True if the associated user to this member is an administrator, False otherwise.
    """
    return user_is_administrator(member.user)


def user_is_administrator(user):
    """
    Check if an user is an administrator of this platform.
    Parameters
    ----------
    user: auth.User to be checked.

    Returns
    -------
    True if the user belongs to administrator groups, False otherwise.
    """
    return user and user.is_authenticated() and user.groups.filter(name=settings.ADMINISTRATOR_GROUP).exists()


# Informs if one user is a member
def user_is_member(user):
    return hasattr(user, "member") and user.member


# Informs if one user is a visitor
def user_is_visitor(user):
    return not user_is_member(user)


# Return the boards of an user
def get_user_boards(user):
    if user_is_member(user):
        return user.member.boards.all().order_by("name")

    if user_is_visitor(user):
        return user.boards.all().order_by("name")

    raise ValueError(u"This user is not valid")