from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import server.settings
from Posts.models import Post
import base64
import requests
from requests.auth import HTTPBasicAuth

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
    
    
def process_images(post, images_urls):
    is_deep_fake = False
    for image_url in images_urls:
        try:
            print(f"Processing image {image_url}")
            image_response = requests.get(image_url)
            image_data = image_response.content
            image_base64 = "data:image/jpeg;base64,"+base64.b64encode(image_data).decode('utf-8')

            api_url = "https://bwsase.bioid.com/extension/passivelivedetection"
            username = "25828e56-b141-4b6e-a2a5-2a751c8f9431"
            password = "2X5h/AKj4pS5PdDAfCX3DHES"
            
            form_data = {
                "image": image_base64
            }         
               
            response = requests.post(
                api_url,
                files=form_data,
                auth=HTTPBasicAuth(username, password)
            )

            response_data = response.json()
            print(response_data.get("Success"))
            if (response_data.get("Success") == False):
                print("FAKE")
                is_deep_fake = True
                post.is_deep_fake = is_deep_fake
                post.deep_fake_details = response_data
                post.save()
                return

        except Exception as e:
            print(f"Error processing image {image_url}: {e}")

