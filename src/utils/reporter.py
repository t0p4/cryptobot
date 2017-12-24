import smtplib
import datetime
from email.mime.text import MIMEText
from src.utils.logger import Logger
log = Logger(__name__)


class Reporter:
    def __init__(self):
        self.server = None
        pass

    def send_report(self, subj, body):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        msg = MIMEText(body)
        msg['Subject'] = subj
        msg['From'] = 'CryptoBot'
        msg['To'] = 'Patrick'
        log.info('Sending report...\n' + msg.as_string())
        self.server.starttls()
        self.server.login("cryptobotreporter@gmail.com", "moonlambosallday")
        self.server.sendmail("cryptobotreporter@gmail.com", "pmckelvy1@gmail.com", msg.as_string())
        self.server.quit()

    def generate_report(self, strats, markets, mkt_tickers):
        market_action_data, something_to_report = self.analyze_strats(strats, markets, mkt_tickers)
        report_body = ""
        if something_to_report:
            for mkt_name, action_data in market_action_data.iteritems():
                if len(action_data) > 0:
                    mkt_report = self.create_mkt_report(mkt_name, action_data)
                    report_body = report_body + "\n" + mkt_report
            subj = "CyrptoBot Market Report: " + datetime.datetime.utcnow().isoformat()
            self.send_report(subj, report_body)

    def create_mkt_report(self, mkt_name, action_data):
        report = "{{<<* * * * * ....." + mkt_name + "..... * * * * *>>}}"
        report += "\n"
        for a_data in action_data:
            report += a_data['strat_name'] + "\n"
            report += a_data['action'] + "\n"
            report += str(a_data['window']) + "\n"
            report += a_data['strat_specific_data'] + "\n"
            report += a_data['recent_data'] + "\n"
            report += "=================================\n"
        report += "\n\n\n"
        return report

    def analyze_strats(self, strats, markets, mkt_tickers):
        market_action_data = dict((m['marketname'], []) for i, m in markets.iterrows())
        something_to_report = False
        for idx, market in markets.iterrows():
            mkt_name = market['marketname']
            mkt_data = mkt_tickers[mkt_name]
            for strat in strats:
                if strat.should_buy(mkt_name) or strat.should_sell(mkt_name):
                    something_to_report = True
                    market_action_data[mkt_name].append(strat.get_mkt_report(mkt_name, mkt_data))
        return market_action_data, something_to_report
