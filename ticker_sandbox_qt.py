from PySide6.QtCharts import QLineSeries, QChart, QChartView
from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QPushButton

from storage_provider import StorageProvider


class Sandbox(QDialog):
    def __init__(self, parent=None):
        super(Sandbox, self).__init__(parent)
        self.setWindowTitle("Sandbox")

        self.symbol_label = QLabel("Symbols")
        self.symbol_selector = QComboBox()
        self.clear_button = QPushButton("Clear Display")
        interactor_layout = self._init_interactors()

        self.chart = QChart()
        self.chart.createDefaultAxes()
        self._line_series = []
        self._chart_view = QChartView(self.chart)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addLayout(interactor_layout)
        main_layout.addLayout(self._init_data_display())
        self.setBaseSize(800, 800)

    def _init_interactors(self):
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(self.symbol_label)
        selector_layout.addWidget(self.symbol_selector)
        box_layout = QVBoxLayout()
        box_layout.addLayout(selector_layout)
        box_layout.addWidget(self.clear_button)
        db = StorageProvider()
        symbols = db.get_all_symbols()
        self.symbol_selector.addItems(symbols)
        self.symbol_selector.currentIndexChanged.connect(self._load_history)
        self.clear_button.clicked.connect(self._clear_display)
        return box_layout

    def _init_data_display(self):
        data_layout = QHBoxLayout()
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        data_layout.addWidget(self._chart_view)
        return data_layout

    def _load_history(self):
        db = StorageProvider()
        ticker = self.symbol_selector.currentText()
        history = db.get_ticker_history(ticker)
        line = QLineSeries()
        line.setName(ticker)

        i = 0
        for date, price in history:
            line.append(QPoint(i, price))
            i += 1

        self._line_series.append(line)
        self.chart.addSeries(line)
        self.chart.createDefaultAxes()

    def _clear_display(self):
        self.chart.removeAllSeries()
