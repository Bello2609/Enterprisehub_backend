import os
import threading
from random import randint
import xlwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponse
from ..members.models import Member
from ..onboarding.models import FrontDesk
from datetime import date, timedelta


class GenerateSheet(threading.Thread):
    def __init__(self, from_date=None, to_date=None, sheet_type=None):
        self.from_date = from_date
        self.to_date = to_date
        self.sheet_type = sheet_type
        threading.Thread.__init__(self)

    def run(self):
        file = generate_sheet(from_date=self.from_date, to_date=self.to_date, sheet_type=self.sheet_type)
        return file


def automated_sheet():
    visitor_file = generate_sheet(from_date=None, to_date=None, sheet_type='visitors', loc='automate')
    member_file = generate_sheet(from_date=None, to_date=None, sheet_type='members', loc='automate')
    virtual_file = generate_sheet(from_date=None, to_date=None, sheet_type='virtual', loc='automate')
    message = 'Please find attached data sheet for the last 30 days'
    mail_subject = 'Enterprise Hubs Automated Data Sheet'
    email_list = ['dozie@pedestalafrica.com', 'nkechi@pedestalafrica.com', 'dozie@icloud.com',
                  'frontoffice@enterprisehubs.com', 'danlanko1@gmail.com']
    email = EmailMessage(mail_subject, message, to=email_list)
    email.attach_file(visitor_file)
    email.attach_file(member_file)
    email.attach_file(virtual_file)
    email.content_subtype = 'html'
    email.send()
    return 'Message sent'


def send_expiry_reminder():
    members = Member.objects.filter(is_active=False)
    today = date.today()
    for member in members:
        expiry_subject = "Enterprise Virtual Office"
        expiry_message = f"Your Virtual Office is expiring on {member.expire_date}"
        delta = today - member.expire_date
        if delta.days <= 7:
            EmailMessage(expiry_subject, expiry_message, to=[member.email]) # Todo .. send auto email on 30, 14, then everyday on 7
        if today == member.expire_date or today > member.expire_date:
            member.is_active = False
            msg = "Your Virtual Office has expired."
            EmailMessage(expiry_subject, msg, to=[member.email])
            member.save()

    return {"Completed"}


def generate_sheet(from_date=None, to_date=None, sheet_type=None, loc=None):
    if from_date is None or to_date is None:
        from_date = date.today() - timedelta(30)
        to_date = date.today()

    if sheet_type == 'visitors':
        front_desk = FrontDesk.objects.filter(date__date__lte=to_date,
                                              date__date__gte=from_date, )
        filename = "%s_from_%s_to_%s_%s.xls" % ('Front_Desk_Data', from_date, to_date,
                                                randint(1, 1000000))
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; %s' % filename
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('sheet1')
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        style0 = xlwt.easyxf('font: name Times New Roman', num_format_str='#,##0.00')

        ws.write(0, 0, 'Front Desk Data - From %s to %s' % (from_date, to_date), font_style)
        ws.write(2, 0, 'Generated On:', font_style)
        ws.write(2, 1, str(date.today()))

        row_num = 4

        columns = ['Name', 'Phone', 'Email', 'Business Name', 'Whom to see', 'Purpose', 'Date']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        x = 1
        data = {}
        for item in front_desk:
            data.update({
                x: [
                    item.name,
                    item.phone,
                    item.email,
                    item.business_name,
                    item.whom_to_see,
                    item.purpose,
                    str(item.date.date()),
                ]
            })
            x += 1

        for item in data.values():
            row_num += 1
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, item[col_num], style0)

        row_num += 2

        path = os.path.join(settings.MEDIA_ROOT, 'report', filename)
        wb.save(path)
        file_path = settings.MEDIA_ROOT + '/report/' + filename
        if loc == 'download':
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + filename
            return response
        else:
            return file_path
    else:
        if sheet_type == 'virtual':
            member = Member.objects.filter(type=4)
            filename = "Virtual_Office_List_Generated_%s_%s.xls" % (date.today(), randint(1, 1000000))
        else:
            member = Member.objects.all()
            filename = "Members_List_Generated_%s_%s.xls" % (date.today(), randint(1, 1000000))
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; %s' % filename
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('sheet1')
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        style0 = xlwt.easyxf('font: name Times New Roman', num_format_str='#,##0.00')

        ws.write(0, 0, 'Member_data-_From_%s_to_%s' % (from_date, to_date), font_style)
        ws.write(2, 0, 'Generated On:', font_style)
        ws.write(2, 1, str(date.today()))

        row_num = 4

        columns = ['Name', 'Phone', 'Email', 'Company Name', 'Membership Type', 'Date Joined', 'Expiring Date',
                   'Status', ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        x = 1
        data = {}
        for item in member:
            data.update({
                x: [
                    item.first_name + ' ' + item.last_name,
                    item.phone,
                    item.email,
                    item.business_name,
                    item.type.name,
                    str(item.date_joined),
                    str(item.expire_date),
                    'Active' if item.is_active else 'Inactive'
                ]
            })
            x += 1

        for item in data.values():
            row_num += 1
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, item[col_num], style0)

        row_num += 2

        path = os.path.join(settings.MEDIA_ROOT, 'report', filename)
        wb.save(path)
        file_path = settings.MEDIA_ROOT + '/report/' + filename
        if loc == 'download':
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = 'inline; filename=' + filename
            return response
        else:
            return file_path
