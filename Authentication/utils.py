from django.core.mail import send_mail
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import secrets
import server.settings

# from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import secrets


def send_email_register(request, email, otp):
    subject = "Verify Your Account - Socius"
    from_email = server.settings.EMAIL_HOST_USER
    to_email = [email]
    print(otp)
    htmldir = (f'{server.settings.BASE_DIR}/templates/Auth/verification_email.html')
    html_content = render_to_string(htmldir,{'otp':otp})
    text_content = strip_tags(html_content)

    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponse("Email sent successfully",status=200)
    except Exception as e:
        print(str(e))
        return HttpResponse("Failed to send email: " + str(e), status=500)
