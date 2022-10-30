from .account.models import UserType
from .members.models import Member
from .staff.models import StaffModel
from .facility.models import Information


def check_user_type(request):

    if request.user.is_authenticated and request.user.is_superuser is False:
        try:
            get_user = UserType.objects.get(user_id=request.user.id).account_type

            return {'user_type': get_user}

        except UserType.DoesNotExist:
            return 'Error'
    else:
        return {}


def check_member_status(request):

    if request.user.is_authenticated and request.user.is_superuser is False:

        if UserType.objects.get(user_id=request.user.id).account_type == 1:
            get_member = Member.objects.get(username=request.user.username)
            check_status = get_member.is_active
            member_id = get_member.member_id

            return {'member_status': check_status, 'member_id': member_id}
        else:
            return {}

    else:
        return {}


def get_staff(request):

    if request.user.is_authenticated and request.user.is_superuser is False:

        try:
            staff = StaffModel.objects.get(user_id=request.user.id)

            return {'staff': staff}

        except StaffModel.DoesNotExist:

            return {}
    else:
        return {}


# Check if user is from head_office
def check_is_oga(request):

    if request.user.is_authenticated and request.user.is_superuser is False:

        try:
            is_oga = StaffModel.objects.get(user_id=request.user.id).is_oga

            return {'is_oga': is_oga}

        except StaffModel.DoesNotExist:

            return {'is_oga': False}
    else:
        return {}


def check_information(request):

    try:
        information = Information.objects.all()

        return {'info': information}

    except Information.DoesNotExist:

        return {'info': None}
