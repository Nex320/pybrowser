import sys
import re
import datetime
import pickle
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, \
    QPushButton, QAction, QMessageBox, QInputDialog, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt



class TabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        self.new_tab_button = QPushButton("+")
        self.new_tab_button.clicked.connect(self.create_new_tab)

        self.setCornerWidget(self.new_tab_button)

    def create_new_tab(self):
        web_view = QWebEngineView()
        web_view.load(QUrl("https://www.google.com"))  # Initial URL to load
        web_view.titleChanged.connect(self.update_tab_title)

        tab_index = self.addTab(web_view, "New Tab")
        self.setCurrentIndex(tab_index)

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)

    def update_tab_title(self, title):
        web_view = self.sender()
        index = self.indexOf(web_view)
        self.setTabText(index, title)


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyBrowser")
        self.setGeometry(100, 100, 800, 600)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Type URL or search here...")
        self.address_bar.returnPressed.connect(self.load_page)
        self.address_bar.setStyleSheet("QLineEdit { background-color: #dcdcdc; }")

        self.backward_button = QPushButton("←")
        self.backward_button.setFixedSize(20, 20)
        self.backward_button.clicked.connect(self.backward)

        self.forward_button = QPushButton("→")
        self.forward_button.setFixedSize(20, 20)
        self.forward_button.clicked.connect(self.forward)

        self.reload_button = QPushButton("↻")
        self.reload_button.setFixedSize(20, 20)
        self.reload_button.clicked.connect(self.reload_page)

        self.home_button = QPushButton("⌂")
        self.home_button.setFixedSize(20, 20)
        self.home_button.clicked.connect(self.go_home)

        self.tabs = TabWidget()
        self.tabs.setDocumentMode(True)

        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("https://www.google.com"))
        self.web_view.urlChanged.connect(self.update_address_bar)
        self.web_view.titleChanged.connect(self.update_tab_title)
        self.web_view.loadFinished.connect(self.save_history)

        self.tabs.addTab(self.web_view, "New Tab")

        address_layout = QHBoxLayout()
        address_layout.addWidget(self.backward_button)
        address_layout.addWidget(self.forward_button)
        address_layout.addWidget(self.reload_button)
        address_layout.addWidget(self.home_button)
        address_layout.addWidget(self.address_bar)

        layout = QVBoxLayout()
        layout.addLayout(address_layout)
        layout.addWidget(self.tabs)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.create_tabs_menu()
        self.create_zoom_menu()
        self.create_help_menu()
        self.create_history_menu()

        self.history_enabled = True  # Set to False to disable history feature and True to enable
        self.history_file = "pyhist"

    def load_page(self):
        current_tab = self.tabs.currentWidget()
        text = self.address_bar.text()
        if re.match(r'^https?://', text):
            url = QUrl.fromUserInput(text)
        else:
            url = QUrl("https://www.google.com/search?q=" + text)
        current_tab.load(url)

    def update_address_bar(self, url):
        self.address_bar.setText(url.toString())

    def update_tab_title(self, title):
        current_tab = self.tabs.currentWidget()
        index = self.tabs.indexOf(current_tab)
        self.tabs.setTabText(index, title)

    def create_tabs_menu(self):
        tabs_menu = self.menuBar().addMenu("Tabs")
        tabs_menu.addAction("New Tab", self.tabs.create_new_tab)

        close_action = QAction("Close Tab", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close_current_tab)
        tabs_menu.addAction(close_action)

    def create_zoom_menu(self):
        zoom_menu = self.menuBar().addMenu("Zoom")

        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        zoom_menu.addAction(zoom_out_action)

        default_zoom_action = QAction("Default Zoom", self)
        default_zoom_action.setShortcut("Ctrl+0")
        default_zoom_action.triggered.connect(self.default_zoom)
        zoom_menu.addAction(default_zoom_action)

    def zoom_in(self):
        current_tab = self.tabs.currentWidget()
        current_tab.setZoomFactor(current_tab.zoomFactor() + 0.1)

    def zoom_out(self):
        current_tab = self.tabs.currentWidget()
        current_tab.setZoomFactor(current_tab.zoomFactor() - 0.1)

    def default_zoom(self):
        current_tab = self.tabs.currentWidget()
        current_tab.setZoomFactor(1.0)

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        self.tabs.close_tab(current_index)

    def create_help_menu(self):
        help_menu = self.menuBar().addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_window)
        help_menu.addAction(about_action)

    def show_about_window(self):
        about_html = '''
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                    }
                    h1 {
                        color: #333333;
                        font-size: 20px;
                        font-weight: bold;
                    }
                    h2 {
                        color: #333333;
                        font-size: 20px;
                        font-weight: normal;
                    }
                </style>
            </head>
            <body>
                    <h1>PyBrowser v2.0</h1>
                    <h2>A simple web browser made in Python with PyQt5.<br>Created by Nex389</h2>
                    <h2>Contributors:<br>Archimax</h2>
                </body>
            </html>
        '''

        about_tab = QWebEngineView()
        about_tab.setHtml(about_html)
        about_tab.titleChanged.connect(self.update_tab_title)

        tab_index = self.tabs.addTab(about_tab, "About")
        self.tabs.setCurrentIndex(tab_index)

    def backward(self):
        current_tab = self.tabs.currentWidget()
        current_tab.back()

    def forward(self):
        current_tab = self.tabs.currentWidget()
        current_tab.forward()

    def reload_page(self):
        current_tab = self.tabs.currentWidget()
        current_tab.reload()

    def go_home(self):
        current_tab = self.tabs.currentWidget()
        current_tab.load(QUrl("https://www.google.com"))

    def create_history_menu(self):
        history_menu = self.menuBar().addMenu("History")

        view_history_action = QAction("View History", self)
        view_history_action.triggered.connect(self.view_history)
        history_menu.addAction(view_history_action)

        clear_history_action = QAction("Clear History", self)
        clear_history_action.triggered.connect(self.clear_history)
        history_menu.addAction(clear_history_action)

    def save_history(self):
        if not self.history_enabled:
            return

        current_tab = self.tabs.currentWidget()
        url = current_tab.url().toString()
        title = current_tab.title()
        timestamp = datetime.datetime.now()

        history_entry = (url, title, timestamp)

        try:
            with open(self.history_file, "ab") as file:
                pickle.dump(history_entry, file)
        except Exception as e:
            print("Error saving history:", str(e))

    def view_history(self):
        if not self.history_enabled:
            return

        try:
            with open(self.history_file, "rb") as file:
                history_entries = []
                while True:
                    try:
                        entry = pickle.load(file)
                        history_entries.append(entry)
                    except EOFError:
                        break

                history_html = '''
                    <html>
                    <head>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                font-size: 14px;
                            }
                            h1 {
                                color: #333333;
                                font-size: 20px;
                                font-weight: bold;
                            }
                            table {
                                border-collapse: collapse;
                                width: 100%;
                            }
                            th, td {
                                padding: 8px;
                                text-align: left;
                                border-bottom: 1px solid #ddd;
                            }
                            .left-align {
                                text-align: left;
                            }
                            .center-align {
                                text-align: center;
                            }
                            .right-align {
                                text-align: right;
                            }
                            .link {
                                word-break: break-all;
                            }
                        </style>
                    </head>
                    <body>
                        <h1>Browser History</h1>
                        <table>
                            <tr>
                                <th>Timestamp</th>
                                <th>Title</th>
                                <th>Website</th>
                            </tr>
                '''

                for entry in history_entries:
                    url, title, timestamp = entry
                    history_html += f'''
                        <tr>
                            <td class="left-align">{timestamp}</td>
                            <td class="center-align">{title}</td>
                            <td class="right-align link"><a href="{url}">{url}</a></td>
                        </tr>
                    '''

                history_html += '''
                        </table>
                    </body>
                    </html>
                '''

                history_tab = QWebEngineView()
                history_tab.setHtml(history_html)
                history_tab.titleChanged.connect(self.update_tab_title)

                tab_index = self.tabs.addTab(history_tab, "History")
                self.tabs.setCurrentIndex(tab_index)

        except FileNotFoundError:
            QMessageBox.information(self, "History", "No history available.")




    def clear_history(self):
        if not self.history_enabled:
            return

        password, ok = QInputDialog.getText(self, "Clear History", "Enter password:", QLineEdit.Password)
        if ok and password == "1234":
            try:
                open(self.history_file, "w").close()
                QMessageBox.information(self, "Clear History", "History cleared successfully.")
            except Exception as e:
                print("Error clearing history:", str(e))
        elif ok:
            QMessageBox.warning(self, "Clear History", "Incorrect password.")
            
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())
