import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(subject, message):
    fromaddr = "robert.zydek.98@wp.pl"
    toaddr = "rzydek@outlook.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.wp.pl', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("robert.zydek.98@wp.pl", "kokobambo1")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
