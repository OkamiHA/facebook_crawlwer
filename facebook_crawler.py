import glob
import json
import os
import random
import time as t
import warnings
import webbrowser

import pandas as pd
import qdarkstyle
import undetected_chromedriver as uc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import *
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys

warnings.filterwarnings('ignore')


class facebook_crawler:
    def __init__(self, username, password, keywords, n_scrolls=50, start=1, co=1):
        self.username = username
        self.password = password
        self.co = co
        self.keywords = keywords
        self.n_scrolls = int(n_scrolls)
        self.posts_text = []
        self.posts_link = []
        self.dates = []
        self.keywords_present = []
        self.start = int(start)
        self.last_saved = int(start)
        try:
            os.mkdir('csv')
        except:
            pass
        try:
            os.mkdir('xlsx')
        except:
            pass

    def scroll_to_the_end(self, pause, c=False):
        if c:
            if self.n_scrolls == -1:
                prev_h = self.driver.execute_script("return document.body.scrollHeight")
                while True:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    t.sleep(round(random.uniform(pause, pause * 2), 1))
                    new_h = self.driver.execute_script("return document.body.scrollHeight")
                    if new_h == prev_h:
                        t.sleep(round(random.uniform(pause, pause + 1), 1) * 3)
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        new_h = self.driver.execute_script("return document.body.scrollHeight")
                        if new_h == prev_h:
                            break
                        else:
                            self.scroll_to_the_end(pause)

                    prev_h = new_h
            else:
                prev_h = self.driver.execute_script("return document.body.scrollHeight")
                for i in range(self.n_scrolls):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    t.sleep(round(random.uniform(pause, pause * 3), 1))
                    new_h = self.driver.execute_script("return document.body.scrollHeight")
                    if new_h == prev_h:
                        t.sleep(pause * 3)
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        new_h = self.driver.execute_script("return document.body.scrollHeight")
                        if new_h == prev_h:
                            break
                        else:
                            pass

                    prev_h = new_h


        else:
            prev_h = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                t.sleep(round(random.uniform(pause, pause * 3), 1))
                new_h = self.driver.execute_script("return document.body.scrollHeight")
                if new_h == prev_h:
                    t.sleep(pause * 3)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    new_h = self.driver.execute_script("return document.body.scrollHeight")
                    if new_h == prev_h:
                        break
                    else:
                        self.scroll_to_the_end(pause)

                prev_h = new_h

    def mobile_login(self):
        username_input = self.driver.find_element_by_id('m_login_email')
        password_input = self.driver.find_element_by_id('m_login_password')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.ENTER)
        self.driver.implicitly_wait(30)
        try:
            ok = self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[2]/div/div[1]/div/div/div[3]/div[2]/form/div/button')
            ok.click()

        except:
            pass

    def mobile_get_groups(self):

        settings = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div[6]/div/a')
        settings.click()
        self.driver.implicitly_wait(30)
        groups = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[2]/div/div[2]/div[6]/div/div/div[1]/div/div/div/div/div/div[1]/ul/li[2]/div/a')
        url = groups.get_attribute('href')
        self.driver.get(url)
        self.driver.implicitly_wait(30)
        groups_ptr = self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[4]/div/div[1]/div/div/div[1]/div/a[2]')
        url = groups_ptr.get_attribute('href')
        self.driver.get(url)
        self.driver.implicitly_wait(30)
        self.scroll_to_the_end(self.co * 1)
        groups_class = self.driver.find_elements_by_class_name('_7hkg')
        self.group_urls = []
        for group in groups_class:
            if group.get_attribute('href') is not None:
                self.group_urls.append(group.get_attribute('href'))
        return self.group_urls

    def get_group_data(self, link):
        self.driver = uc.Chrome()
        self.driver.get('https://mobile.facebook.com')
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.mobile_login()
        self.driver.implicitly_wait(30)
        link = link.replace('www.facebook', 'm.facebook').replace('web.facebook', 'm.facebook')
        self.driver.get(link)
        self.driver.implicitly_wait(30)
        self.scroll_to_the_end(self.co * 2)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        try:
            title = soup.find('a', {"class": "_6j_c"}).get_text()
        except:
            title = 'group_1'
        posts = soup.find_all("div", {"class": "story_body_container"})
        for post_main in posts:
            post = post_main.find("div", {"class": "_5rgt _5nk5 _5wnf _5msi"})
            try:
                text = post.get_text()
            except:
                text = ''
            try:
                extra_text = ''
                extra_texts = post.findall("span", {"class": "text_exposed_show"})
                for tt in extra_texts:
                    extra_text += tt.get_text() + ' '
            except:
                extra_text = ''
            f_text = ''
            if len(text) + len(extra_text) > 0:
                f_text = text + ' ' + extra_text
            p = []
            for i in self.keywords:
                l = len(i.split())
                if len(f_text) > l:
                    for ind in range(0, len(f_text.split()) - (l - 1)):
                        jj = text.split()[ind:ind + l]
                        j = ' '
                        j = j.join(jj)
                        if j.isalpha():
                            if i.lower() == j.lower():
                                p.append(i)
                                break
                            else:
                                if i == j:
                                    p.append(i)
                                    break

            if len(p) > 0:
                try:
                    post_url = post_main.find("a", {"class": "_39pi"}, href=True)['href']
                    if not post_url.startswith('https'):
                        post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                    if post_url is None:
                        post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                    else:
                        post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                except:
                    try:
                        post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                    except:

                        post_url = ''
                try:
                    post_date = post_main.find("div", {"class": "_52jc _5qc4 _78cz _24u0 _36xo"}).get_text()
                except:
                    post_date = ''
                if post_url.startswith('https'):
                    self.posts_text.append(f_text)
                    self.posts_link.append(post_url.replace('m.facebook.com', 'www.facebook.com'))
                    self.dates.append(post_date)
                    self.keywords_present.append(p)
        df = pd.DataFrame()
        df['text'] = self.posts_text
        df['links'] = self.posts_link
        df['date'] = self.dates
        df['keywords found'] = self.keywords_present
        df.to_excel(f'xlsx//{self.username}_posts_{title}.xlsx')
        df.to_csv(f'csv//{self.username}_posts_{title}.csv')

    def new_scraper(self):

        self.driver = uc.Chrome()
        self.driver.get('https://mobile.facebook.com')
        self.driver.maximize_window()
        self.driver.implicitly_wait(30)
        self.mobile_login()
        self.driver.implicitly_wait(30)
        urls = self.mobile_get_groups()

        for index, group in enumerate(self.group_urls):
            if index + 1 >= self.start:

                t.sleep(round(random.uniform(5, 15), 1))
                self.driver.get(group)
                self.driver.implicitly_wait(30)
                try:
                    error = self.driver.find_element_by_xpath(
                        '/html/body/div[1]/div/div[4]/div/div[1]/div[1]/span/div').text
                    if 'It looks like you were misusing this feature by going too fast. You’ve been temporarily blocked' in error:
                        self.driver.close()
                        self.save_excel(index)

                #       pass
                except:
                    pass
                self.driver.implicitly_wait(30)
                self.scroll_to_the_end(self.co * 4, c=True)
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                posts = soup.find_all("div", {"class": "story_body_container"})
                for post_main in posts:
                    post = post_main.find("div", {"class": "_5rgt _5nk5 _5wnf _5msi"})
                    try:
                        text = post.get_text()
                    except:
                        text = ''
                    try:
                        extra_text = ''
                        extra_texts = post.findall("span", {"class": "text_exposed_show"})
                        for tt in extra_texts:
                            extra_text += tt.get_text() + ' '
                    except:
                        extra_text = ''
                    f_text = ''
                    if len(text) + len(extra_text) > 0:
                        f_text = text + ' ' + extra_text
                    p = []
                    for i in self.keywords:
                        l = len(i.split())
                        if len(f_text) > l:
                            for ind in range(0, len(f_text.split()) - (l - 1)):
                                jj = text.split()[ind:ind + l]
                                j = ' '
                                j = j.join(jj)
                                if j.isalpha():
                                    if i.lower() == j.lower():
                                        p.append(i)
                                        break
                                    else:
                                        if i == j:
                                            p.append(i)
                                            break

                    if len(p) > 0:
                        try:
                            post_url = post_main.find("a", {"class": "_39pi"}, href=True)['href']
                            if not post_url.startswith('https'):
                                post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                            if post_url is None:
                                post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                            else:
                                post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                        except:
                            try:
                                post_url = post_main.find("a", {"class": "_5msj"}, href=True)['href']
                            except:

                                post_url = ''
                        try:
                            post_date = post_main.find("div", {"class": "_52jc _5qc4 _78cz _24u0 _36xo"}).get_text()
                        except:
                            post_date = ''
                        if post_url.startswith('https'):
                            self.posts_text.append(f_text)
                            self.posts_link.append(post_url)
                            self.dates.append(post_date)
                            self.keywords_present.append(p)
                            # print(post_url)
                            # print(post_date)
                            # print(f_text)
                            # print(p,end='\n\n\n')

                if (index + 1) % 10 == 0 or (index + 1) == len(self.group_urls):
                    self.save_excel(index)
                    t.sleep(round(random.uniform(10 * 60, 11 * 60), 1))

        self.driver.close()

    def save_excel(self, index):
        df = pd.DataFrame()
        df['text'] = self.posts_text
        df['links'] = self.posts_link
        df['date'] = self.dates
        df['keywords found'] = self.keywords_present
        self.posts_text = []
        self.dates = []
        self.posts_link = []
        self.keywords_present = []
        if index + 1 == len(self.group_urls):
            df.to_csv(f'csv//{self.username}_posts_groups_from_{self.last_saved}_to_{index + 1}_final.csv')
            df.to_excel(f'xlsx//{self.username}_posts_groups_from_{self.last_saved}_to_{index + 1}_final.xlsx')
        else:
            df.to_csv(f'csv//{self.username}_posts_groups_from_{self.last_saved}_to_{index + 1}.csv')
            df.to_excel(f'xlsx//{self.username}_posts_groups_from_{self.last_saved}_to_{index + 1}.xlsx')
        self.last_saved = index + 1


class worker(QObject):
    def crawl(self, info):
        try:
            username, password, keywords, n_scrolls, start = info
            crawler = facebook_crawler(username, password, keywords, n_scrolls, start, 1)
            crawler.new_scraper()
        except:
            pass

    def crawl_group(self, info):
        username, password, keywords, n_scrolls, group_link = info
        crawler = facebook_crawler(username, password, keywords, n_scrolls)
        crawler.get_group_data(group_link)


class Main_Window(qtw.QWidget):
    sig = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facebook Group Crawler")
        self.resize(700, 500)
        self.email = qtw.QLineEdit()
        self.email_label = qtw.QLabel('Enter Facbook Email:')
        self.email_label.setStyleSheet(self.label_style())
        self.email.setStyleSheet(self.line_edit_style())
        self.password = qtw.QLineEdit()
        self.password.setEchoMode(qtw.QLineEdit.Password)
        self.start_gp = qtw.QLineEdit()
        self.start_gp.setStyleSheet(self.line_edit_style())
        self.start_label = qtw.QLabel('Enter which group you want to start from:')
        self.start_label.setStyleSheet(self.label_style())

        self.password_label = qtw.QLabel('Enter Facbook Password:')
        self.password_label.setStyleSheet(self.label_style())
        self.password.setStyleSheet(self.line_edit_style())
        self.keywords = qtw.QLineEdit()
        self.keywords_label = qtw.QLabel('Enter Keyword You Want To Add Here:')
        self.keywords_label.setStyleSheet(self.label_style())

        self.keywords.setStyleSheet(self.line_edit_style())
        self.keywords.editingFinished.connect(self.add_word)
        self.range = qtw.QLineEdit()
        self.range_label = qtw.QLabel('Enter max number of scrolls:')
        self.range_label.setStyleSheet(self.label_style())

        self.range.setStyleSheet(self.line_edit_style())
        self.range.setToolTip('for infinite scrolls enter -1')
        self.submit = qtw.QPushButton("submit")
        self.submit.setIcon(qtg.QIcon(qtg.QPixmap('facebook.png')))
        self.clear = qtw.QPushButton("Clear")
        self.clear.clicked.connect(self.clear_list)
        self.clear.setStyleSheet(self.button_style())
        self.remove_keyword = qtw.QPushButton('remove')
        self.remove_keyword.clicked.connect(self.remove_word)
        self.remove_keyword.setStyleSheet(self.button_style())
        self.keywords_list = qtw.QListWidget()
        self.add_keyword = qtw.QPushButton('Add keyword')
        self.add_keyword.setStyleSheet(self.button_style())
        self.add_keyword.clicked.connect(self.add_word)
        self.submit.setStyleSheet(self.button_style())
        self.submit.clicked.connect(self.start_crawling)
        self.group = qtw.QLineEdit()
        self.group.setStyleSheet(self.line_edit_style())
        self.group_label = qtw.QLabel('For scrapping one group enter group link here:')
        self.group_label.setStyleSheet(self.label_style())
        self.get_group = qtw.QPushButton('get 1 group data')
        self.get_group.setStyleSheet(self.button_style())
        self.get_group.clicked.connect(self.crawl_group)
        self.view_tabel = qtw.QPushButton('Click to view data')
        self.view_tabel.setStyleSheet(self.button_style())
        self.view_tabel.clicked.connect(self.go_to_tabele)
        #########
        self.return_btn = qtw.QPushButton('Click to return to main page')
        self.return_btn.setStyleSheet(self.button_style())
        self.return_btn.clicked.connect(self.ret_main_page)

        self.load_data = qtw.QPushButton('load_data')
        self.load_data.setStyleSheet(self.button_style())
        self.load_data.clicked.connect(self.load_facebook_data)
        self.tabel = qtw.QTableWidget(2, 4)
        self.tabel.setColumnWidth(0, 400)
        self.tabel.setColumnWidth(1, 400)
        self.tabel.setColumnWidth(2, 100)
        self.tabel.setColumnWidth(3, 100)
        self.tabel.setHorizontalHeaderLabels(["Text", "urls", "date", "keywords"])
        self.tabel.itemDoubleClicked.connect(self.visit)

        try:
            with open('recent.json') as f:
                recent = json.load(f)
                self.email.setText(recent['username'])
            for k in recent['keywords']:
                self.keywords_list.addItem(qtw.QListWidgetItem(k, self.keywords_list))
        except:
            pass

        self.setup_layout()

    def ret_main_page(self):
        self.stly.setCurrentIndex(0)

    def load_facebook_data(self):
        files = glob.glob('csv//*.csv')
        my_list = []
        for file in files:
            df = pd.read_csv(file)
            for j in range(len(df['text'])):
                text = df['text'][j]
                link = df['links'][j]
                date = df['date'][j]
                keyword = df['keywords found'][j]
                my_list.append([text, link, date, keyword])
        self.resize(1200, 500)
        self.tabel.setRowCount(len(my_list))
        for ind, i in enumerate(my_list):
            text, link, date, keyword = i
            self.tabel.setItem(ind, 0, qtw.QTableWidgetItem(str(text)))
            link = str(link.replace('m.facebook.com', 'www.facebook.com'))
            self.tabel.setItem(ind, 1, qtw.QTableWidgetItem(link))
            self.tabel.item(ind, 1).setForeground(qtg.QBrush(qtg.QColor(0, 0, 255)))
            self.tabel.setItem(ind, 2, qtw.QTableWidgetItem(str(date)))
            self.tabel.setItem(ind, 3, qtw.QTableWidgetItem(str(keyword)))

    def visit(self, item):
        if item.column() == 1:
            webbrowser.open_new_tab(item.text())

    def go_to_tabele(self):
        self.stly.setCurrentIndex(1)

    def crawl_group(self):
        self.thread = QThread()
        self.worker_1 = worker()
        self.worker_1.moveToThread(self.thread)
        self.sig.connect(self.worker_1.crawl_group)
        self.thread.start()
        l = []
        for i in range(self.keywords_list.count()):
            l.append(self.keywords_list.item(i).text())
        info = (self.email.text(), self.password.text(), l, self.range.text(), self.group.text())
        self.sig.emit(info)

    def closeEvent(self, event):
        l = []
        for i in range(self.keywords_list.count()):
            l.append(self.keywords_list.item(i).text())
        my_dict = {"username": self.email.text(), "keywords": l}
        with open('recent.json', 'w') as fp:
            json.dump(my_dict, fp)

        event.accept()

    def clear_list(self):
        self.keywords_list.clear()

    def label_style(self):
        return '''QLabel{
        color:white;
        font:bold 12px;
        min-width=5em;
        }
        '''

    def remove_word(self):
        self.items = self.keywords_list.selectedItems()
        for item in self.items:
            QLWI = self.keywords_list.takeItem(self.keywords_list.row(item))

    def add_word(self):
        self.keywords_list.addItem(qtw.QListWidgetItem(self.keywords.text(), self.keywords_list))
        self.keywords.setText('')

    def line_edit_style(self):
        return '''
        color:white;
        min-height:2em;
        border-radius:5px;
        font:bold 14px;
        min-width:25em
        '''

    def button_style(self):
        s = """
        QPushButton{
            background-color:blue;
            color:white;
            border-radius:10px;
            min-width:14em;
            min-height:2em;
            font:bold 14px;
        }

        QPushButton::hover{
            background-color:rgb(50,250,250);
            color:white;
            border-radius:10px;
            min-width:14em;
            min-height:3em;
            font:bold 14px;
        }


        """
        return s

    def setup_layout(self):
        self.main_w = qtw.QWidget()
        self.stly = qtw.QStackedLayout()
        self.mainlayout = qtw.QHBoxLayout()
        self.left_layout = qtw.QVBoxLayout()
        self.left_layout.addWidget(self.email_label)
        self.left_layout.addWidget(self.email)
        self.left_layout.addStretch()
        self.left_layout.addWidget(self.password_label)
        self.left_layout.addWidget(self.password)
        self.left_layout.addStretch()
        self.left_layout.addWidget(self.range_label)
        self.left_layout.addWidget(self.range)
        self.left_layout.addStretch()
        self.left_layout.addWidget(self.start_label)
        self.left_layout.addWidget(self.start_gp)
        self.left_layout.addStretch()
        self.left_layout.addWidget(self.submit)
        self.left_layout.addWidget(self.view_tabel)

        self.one_gp_ly = qtw.QVBoxLayout()
        self.one_gp_ly.addWidget(self.group_label)
        self.one_gp_ly.addWidget(self.group)
        self.one_gp_ly.addWidget(self.get_group)
        self.left_layout.addLayout(self.one_gp_ly)
        self.mainlayout.addLayout(self.left_layout)
        self.right_layout = qtw.QVBoxLayout()
        self.right_layout.addWidget(self.keywords_list)
        self.right_layout.addWidget(self.keywords_label)
        self.right_layout.addWidget(self.keywords)
        self.buttons_layout = qtw.QHBoxLayout()
        self.buttons_layout.addWidget(self.add_keyword)
        self.buttons_layout.addWidget(self.remove_keyword)
        self.buttons_layout.addWidget(self.clear)
        self.right_layout.addLayout(self.buttons_layout)
        self.mainlayout.addLayout(self.right_layout)
        self.main_w.setLayout(self.mainlayout)
        ###############################
        self.tabel_ly = qtw.QVBoxLayout()
        self.tabel_ly_w = qtw.QWidget()
        self.h_ly = qtw.QHBoxLayout()
        self.h_ly.addStretch()
        self.h_ly.addWidget(self.return_btn)
        self.h_ly.addStretch()
        self.h_ly.addWidget(self.load_data)
        self.h_ly.addStretch()
        self.tabel_ly.addLayout(self.h_ly)
        self.tabel_ly.addWidget(self.tabel)
        self.tabel_ly_w.setLayout(self.tabel_ly)

        self.stly.addWidget(self.main_w)
        self.stly.addWidget(self.tabel_ly_w)
        self.setLayout(self.stly)
        self.stly.setCurrentIndex(0)
        self.show()

    def start_crawling(self):
        self.thread = QThread()
        self.worker_1 = worker()
        self.worker_1.moveToThread(self.thread)
        self.sig.connect(self.worker_1.crawl)
        self.thread.start()
        l = []
        for i in range(self.keywords_list.count()):
            l.append(self.keywords_list.item(i).text())
        info = (self.email.text(), self.password.text(), l, self.range.text(), self.start_gp.text())
        self.sig.emit(info)


app = qtw.QApplication([])
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
mw = Main_Window()
app.exec_()
