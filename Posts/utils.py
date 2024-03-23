from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import server.settings
from Posts.models import Post

def send_email_post_warning(request, email, post):
    post = Post.objects.get(id=post)
    subject = "Post Reported Warning - Socius"
    from_email = server.settings.EMAIL_HOST_USER
    to_email = [email]
    guidelines_url = request.build_absolute_uri('/community-guidelines/')  

    # Render the HTML template
    html_content = render_to_string('Report/post_reported.html', {
        'user': post.user,
        'post': post,
        'guidelines_url': guidelines_url,
    })

    try:
        msg = EmailMultiAlternatives(subject, None, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponse("Email sent successfully", status=200)
    except Exception as e:
        print(str(e))
        return HttpResponse("Failed to send email: " + str(e), status=500)