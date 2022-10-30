from django.core.mail import EmailMessage
from django.core.management import BaseCommand

from apps.helpers.services import generate_sheet


class Command(BaseCommand):
    help = 'Auto send report to email'

    def handle(self, *args, **options):
        try:
            visitor_file = generate_sheet(from_date=None, to_date=None, sheet_type='visitors', loc='automate')
            member_file = generate_sheet(from_date=None, to_date=None, sheet_type='members', loc='automate')
            virtual_office = generate_sheet(from_date=None, to_date=None, sheet_type='virtual', loc='automate')
            message = 'Please find attached data sheet for the last 30 days'
            mail_subject = 'Enterprise Hubs Automated Data Sheet'
            email_list = ['dozie@pedestalafrica.com', 'nkechi@pedestalafrica.com', 'dozie@icloud.com',
                          'frontoffice@enterprisehubs.com', 'danlanko1@gmail.com']
            # email_list = ['danlanko1@gmail.com']
            email = EmailMessage(mail_subject, message, to=email_list)
            email.attach_file(visitor_file)
            email.attach_file(member_file)
            email.attach_file(virtual_office)
            email.content_subtype = 'html'
            email.send()
            return 'Message sent'
        except Exception as error:
            pass