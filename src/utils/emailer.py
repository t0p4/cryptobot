import smtplib
from email.mime.text import MIMEText
from src.utils.logger import Logger
log = Logger(__name__)


class Reporter:
    def __init__(self):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)

    def send_report(self, subj, body):
        msg = MIMEText(body)
        msg['Subject'] = subj
        msg['From'] = 'CryptoBot'
        msg['To'] = 'Patrick'
        log.info('Sending report...\n' + msg.as_string())
        self.server.starttls()
        self.server.login("cryptobotreporter@gmail.com", "moonlambosallday")
        self.server.sendmail("cryptobotreporter@gmail.com", "pmckelvy1@gmail.com", msg.as_string())
        self.server.quit()