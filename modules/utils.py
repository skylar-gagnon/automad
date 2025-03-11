import sys, smtplib, json, traceback
from email.message import EmailMessage

def throw_error(err_msg):
        sys.stderr.write("Error: " + err_msg)
        exit(1)

def notif_failure(name, exc_info, config_name):
    subject = f"{name} Failed"
    tb = '\n'.join(traceback.format_exception(exc_info[1]))
    content = f"Experiment failed due to {exc_info[0].__name__}.\n\nTraceback: {tb}"
    with open(config_name, "r") as file:
        email_info = json.load(file)

    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = email_info["from"]
    msg['To'] = email_info["to"]

    s = smtplib.SMTP(email_info["smtp_server"], email_info["port"])
    s.starttls()
    s.login(email_info["from"], email_info["password"])
    s.send_message(msg)
    s.quit()