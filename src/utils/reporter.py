import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from email.MIMEText import MIMEText
from email.mime.image import MIMEImage
from src.utils.logger import Logger
import matplotlib.pyplot as plt
import pandas as pd
from pandas.tools.plotting import table
from src.utils.plotter import Plotter
log = Logger(__name__)


class Reporter:
    def __init__(self):
        self.server = None
        self.plotter = Plotter()
        pass

    def send_report(self, subj, body, images):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        msg = MIMEMultipart('CRYPTOALERT!')
        msg['Subject'] = subj
        msg['From'] = 'CryptoBot'
        msg['To'] = 'Patrick'

        # create multipart
        msg_alt = MIMEMultipart()
        msg.attach(msg_alt)

        # attach HTML body
        msg_txt = MIMEText(body, 'html')
        msg_alt.attach(msg_txt)

        # attach images
        for img_meta_data in images:
            # get image from current directory
            fp = open(img_meta_data['file_path'] + img_meta_data['file_name'] + img_meta_data['file_ext'], 'rb')
            msg_img = MIMEImage(fp.read())
            fp.close()
            msg_img.add_header('Content-ID', '<' + img_meta_data['file_name'] + '>')
            msg.attach(msg_img)

        log.info('Sending report...\n')
        self.server.starttls()
        self.server.login("cryptobotreporter@gmail.com", "moonlambosallday")
        self.server.sendmail("cryptobotreporter@gmail.com", "pmckelvy1@gmail.com", msg.as_string())
        self.server.quit()

    def generate_report(self, strats, markets, mkt_tickers):
        market_action_data, something_to_report = self.analyze_strats(strats, markets, mkt_tickers)
        report_body = ""
        report_images = []
        if something_to_report:
            for mkt_name, action_data in market_action_data.iteritems():
                if len(action_data['strat_data']) > 0:
                    mkt_report = self.create_mkt_report(mkt_name, action_data)
                    report_body = report_body + "\n" + mkt_report
                    report_images.append(action_data['plot_file_meta_data'])
            subj = "CyrptoBot Market Report: " + datetime.datetime.utcnow().isoformat()
            self.send_report(subj, report_body, report_images)

    def create_mkt_report(self, mkt_name, action_data):
        report = "<b>* * * * * ....." + mkt_name + "..... * * * * *</b><br>"
        for strat_data in action_data['strat_data']:
            report += "<pre>"
            report += strat_data['strat_name'] + " :: " + strat_data['action'] + " :: window = " + str(strat_data['window']) + "\n"
            report += strat_data['strat_specific_data']
            # report += a_data['recent_data'] + "\n"
            report += "\n=================================\n"
            report += "</pre>"
        report += '<br><img src="cid:' + action_data['plot_file_meta_data']['file_name'] + '"><br><br><br>'
        return report

    def analyze_strats(self, strats, markets, mkt_tickers):
        market_action_data = dict((m['marketname'], {'plot_name': '', 'strat_data': []}) for i, m in markets.iterrows())
        something_to_report = False
        for idx, market in markets.iterrows():
            mkt_name = market['marketname']
            mkt_data = mkt_tickers[mkt_name]
            for strat in strats:
                if strat.should_buy(mkt_name) or strat.should_sell(mkt_name):
                    something_to_report = True
                    action_data = strat.get_mkt_report(mkt_name, mkt_data)
                    plot_file_meta_data = self.plotter.plot_market(mkt_name, mkt_data, pd.DataFrame(), [strat], save_plot=True, show_plot=False)
                    market_action_data[mkt_name]['strat_data'].append(action_data)
                    market_action_data[mkt_name]['plot_file_meta_data'] = plot_file_meta_data
        return market_action_data, something_to_report
