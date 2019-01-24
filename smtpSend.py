import smtplib
import email.mime.multipart
import email.mime.text
from spider.config import SMTP_USER, SMTP_PASS


def SmtpSender(title, content, receiver):
    msg = email.mime.multipart.MIMEMultipart()
    login_user = SMTP_USER
    login_pass = SMTP_PASS
    receiver = receiver

    msg['Subject'] = title
    msg['From'] = login_user
    msg['To'] = receiver
    content = u"详情:\n {}".format(content)
    txt = email.mime.text.MIMEText(content, "plain", "utf-8")
    msg.attach(txt)

    # smtp = smtplib
    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com', '25')
    smtp.login(login_user, login_pass)
    smtp.sendmail(login_user, receiver, msg.as_string())
    smtp.quit()
    print("Receiver {} Send Success!!".format(receiver))


# SmtpSender("aa", "bb")