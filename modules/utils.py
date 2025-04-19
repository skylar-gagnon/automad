import sys, smtplib, json, traceback, pprint
from email.message import EmailMessage
from datetime import datetime

def throw_error(err_msg):
        sys.stderr.write("Error: " + err_msg)
        exit(1)

def runtime2sec(runtime):
    time = int(runtime[:-1])
    unit = runtime[-1]
    match unit:
        case 's':
            return time
        case 'm':
            return time * 60
        case 'h':
            return time * 60 * 60
        case _:
            throw_error("invalid unit for runtime")

def notif_failure(name, exc_info, config_path):
    subject = f"{name} Failed"
    tb = '\n'.join(traceback.format_exception(exc_info[1]))
    content = f"Experiment failed due to {exc_info[0].__name__}.\n\nTraceback: {tb}"
    with open(config_path, "r") as file:
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

def print_launch_msg(config):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Run Details:\n{pprint.pformat(config)} \n--------------------------------\nLaunching AutoMAD at {now}.")
        return now

def print_exit_msg(status):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if status == 1:
            print(f"--------------------------------\nAutoMAD run FAILED. Exiting at {now}.")
        else:
            print(f"--------------------------------\nAutoMAD exiting at {now}.")

class SSHError(Exception):
    pass