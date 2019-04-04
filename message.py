# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib


def send_message(subject, message, address):
    # Define these once; use them twice!
    str_from =  "robert.zydek.98@wp.pl"
    str_to = address

    # Create the root message and fill in the from, to, and subject headers
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = 'test message'
    msg_root['From'] = str_from
    msg_root['To'] = str_to
    msg_root.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    msg_text = MIMEText('This is the alternative plain text message.')
    msg_alternative.attach(msg_text)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    with open('email/text.txt') as f:
        text = f.read()
        print(text)
        msg_text = MIMEText(text.rstrip(), 'html')
        msg_alternative.attach(msg_text)

    # This example assumes the image is in the current directory
    fp = open('email/logo.png', 'rb')
    msg_image = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msg_image.add_header('Content-ID', '<image1>')
    msg_root.attach(msg_image)

    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP()
    smtp.connect('smtp.wp.pl', 587)
    smtp.login("robert.zydek.98@wp.pl", "kokobambo1")
    smtp.sendmail(str_from, str_to, msg_root.as_string())
    smtp.quit()


# send_message('Message with html and image', '', 'rzydek@outlook.com')

with open('email/text.txt', 'r') as f:
    print(f.read())
