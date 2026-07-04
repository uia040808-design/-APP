"""
晚秋记账 - 个人记账应用
Python + PyQt6 + SQLite + Matplotlib
"""
import sys
import os
import sqlite3
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QStackedWidget, QHeaderView, QMessageBox, QDialog, QFormLayout,
    QDateEdit, QTextEdit, QFrame, QGridLayout, QDialogButtonBox,
    QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction

# Matplotlib for pie chart
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ============================================
# 全局颜色常量（现代秋日暖色系）
# ============================================
class Colors:
    """设计系统颜色定义。通俗解释：把所有颜色集中管理，方便统一调整"""
    # 侧边栏
    SIDEBAR_BG = "#1c1917"          # 侧边栏背景（接近纯黑的暖色调）
    SIDEBAR_TEXT = "#d4cfc9"        # 侧边栏文字
    SIDEBAR_TEXT_MUTED = "#8c8279"  # 侧边栏次要文字
    SIDEBAR_HOVER = "rgba(255,255,255,0.06)"  # 侧边栏悬停
    SIDEBAR_ACTIVE_BAR = "#e67e22"  # 激活态左侧竖条

    # 主内容区
    PAGE_BG = "#f9f7f4"             # 页面背景（暖白）
    CARD_BG = "#ffffff"             # 卡片背景
    CARD_BORDER = "#ede8e2"         # 卡片边框

    # 文字
    TEXT_PRIMARY = "#1c1917"        # 主文字
    TEXT_SECONDARY = "#8c7b6b"      # 次要文字
    TEXT_MUTED = "#b8a99a"          # 更淡的文字

    # 主题色
    ACCENT = "#e67e22"              # 主题橙色
    ACCENT_HOVER = "#d35400"        # 悬停加深
    ACCENT_LIGHT = "#fef5eb"        # 橙色浅底

    # 功能色
    DANGER = "#c0392b"              # 删除/危险
    SUCCESS = "#27ae60"             # 收入/成功

    # 输入框
    INPUT_BORDER = "#e0d6c8"        # 输入框边框
    INPUT_FOCUS = "#e67e22"         # 输入框聚焦


def shadow(blur=25, offset=(0, 3), alpha=8):
    """
    创建柔和阴影效果。
    注：PyQt6 的 QSS 不支持 box-shadow，需要用 QGraphicsDropShadowEffect 实现。
    """
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(*offset)
    effect.setColor(QColor(0, 0, 0, alpha))
    return effect


# ============================================
# 全局样式表（QSS — 类似网页 CSS 的 Qt 样式语言）
# ============================================
GLOBAL_QSS = f"""
/* === 全局基础 === */
QMainWindow {{
    background-color: {Colors.PAGE_BG};
}}

QWidget {{
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    color: {Colors.TEXT_PRIMARY};
}}

/* === 全局输入框 === */
QLineEdit, QComboBox, QDateEdit, QTextEdit {{
    padding: 10px 14px;
    border: 1.5px solid {Colors.INPUT_BORDER};
    border-radius: 10px;
    background: #ffffff;
    font-size: 15px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_LIGHT};
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border-color: {Colors.ACCENT};
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid {Colors.INPUT_BORDER};
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}}

QComboBox QAbstractItemView {{
    background: #fff;
    border: 1px solid {Colors.CARD_BORDER};
    border-radius: 8px;
    padding: 6px;
    selection-background-color: {Colors.ACCENT_LIGHT};
    selection-color: {Colors.TEXT_PRIMARY};
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border-radius: 6px;
}}

/* === 日期编辑框的下拉按钮 === */
QDateEdit::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid {Colors.INPUT_BORDER};
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}}

/* === 滚动条 === */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #d4c5b2;
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: #b8a08a;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
}}

QScrollBar::handle:horizontal {{
    background: #d4c5b2;
    border-radius: 4px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #b8a08a;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* === 表格通用 === */
QTableWidget {{
    background: #ffffff;
    border: 1px solid {Colors.CARD_BORDER};
    border-radius: 12px;
    gridline-color: transparent;
    selection-background-color: {Colors.ACCENT_LIGHT};
    selection-color: {Colors.TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 10px 14px;
    border-bottom: 1px solid #f5f0e9;
}}

QHeaderView::section {{
    background: #fdf9f3;
    color: {Colors.TEXT_SECONDARY};
    font-size: 13px;
    font-weight: bold;
    padding: 14px;
    border: none;
    border-bottom: 2px solid {Colors.CARD_BORDER};
    letter-spacing: 0.3px;
}}

/* === 消息框 === */
QMessageBox {{
    background: #ffffff;
}}

QMessageBox QPushButton {{
    padding: 8px 20px;
    border-radius: 8px;
    font-size: 14px;
    min-width: 80px;
}}
"""


# ============================================
# 数据库管理（完全不变）
# ============================================
class Database:
    def __init__(self):
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        db_dir = os.path.join(appdata, '晚秋记账')
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, 'data.db')
        self.init_db()

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def init_db(self):
        conn = self.get_conn()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                icon TEXT NOT NULL,
                is_default INTEGER DEFAULT 0
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
                category TEXT NOT NULL,
                sub_category TEXT DEFAULT '',
                note TEXT DEFAULT '',
                date TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now', 'localtime'))
            )
        ''')
        count = conn.execute('SELECT COUNT(*) as cnt FROM categories').fetchone()
        if count['cnt'] == 0:
            defaults = [
                ('餐饮', '🍜'), ('交通', '🚌'), ('住房', '🏠'), ('服饰', '👗'),
                ('医疗', '🏥'), ('通讯', '📱'), ('娱乐', '🎮'), ('学习', '📚'),
                ('人情', '🎁'), ('工作', '💼'), ('收入', '💰'), ('其他', '🔧')
            ]
            conn.executemany(
                'INSERT INTO categories (name, icon, is_default) VALUES (?, ?, 1)',
                defaults
            )
        conn.commit()
        conn.close()

    def get_categories(self):
        conn = self.get_conn()
        rows = conn.execute('SELECT * FROM categories ORDER BY id').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_category(self, name, icon):
        conn = self.get_conn()
        cur = conn.execute('INSERT INTO categories (name, icon) VALUES (?, ?)', (name, icon))
        conn.commit()
        cat_id = cur.lastrowid
        conn.close()
        return {'id': cat_id, 'name': name, 'icon': icon}

    def delete_category(self, cat_id):
        conn = self.get_conn()
        conn.execute('DELETE FROM categories WHERE id = ? AND is_default = 0', (cat_id,))
        conn.commit()
        conn.close()

    def update_category(self, cat_id, name, icon):
        """更新分类名称和图标（仅限非预置分类）"""
        conn = self.get_conn()
        conn.execute(
            'UPDATE categories SET name = ?, icon = ? WHERE id = ? AND is_default = 0',
            (name, icon, cat_id)
        )
        conn.commit()
        conn.close()

    def add_record(self, amount, rtype, category, sub_category, note, date):
        conn = self.get_conn()
        cur = conn.execute(
            'INSERT INTO records (amount, type, category, sub_category, note, date) VALUES (?, ?, ?, ?, ?, ?)',
            (amount, rtype, category, sub_category or '', note or '', date)
        )
        conn.commit()
        rec_id = cur.lastrowid
        conn.close()
        return rec_id

    def update_record(self, rec_id, amount, rtype, category, sub_category, note, date):
        conn = self.get_conn()
        conn.execute(
            'UPDATE records SET amount=?, type=?, category=?, sub_category=?, note=?, date=? WHERE id=?',
            (amount, rtype, category, sub_category or '', note or '', date, rec_id)
        )
        conn.commit()
        conn.close()

    def delete_record(self, rec_id):
        conn = self.get_conn()
        conn.execute('DELETE FROM records WHERE id = ?', (rec_id,))
        conn.commit()
        conn.close()

    def get_records(self, month=None):
        conn = self.get_conn()
        if month:
            rows = conn.execute(
                "SELECT * FROM records WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC, id DESC",
                (month,)
            ).fetchall()
        else:
            rows = conn.execute('SELECT * FROM records ORDER BY date DESC, id DESC').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_monthly_stats(self, month):
        conn = self.get_conn()
        expense_stats = conn.execute('''
            SELECT category, SUM(amount) as total
            FROM records
            WHERE type = 'expense' AND strftime('%Y-%m', date) = ?
            GROUP BY category ORDER BY total DESC
        ''', (month,)).fetchall()
        income_total = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM records WHERE type = 'income' AND strftime('%Y-%m', date) = ?
        ''', (month,)).fetchone()['total']
        expense_total = conn.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM records WHERE type = 'expense' AND strftime('%Y-%m', date) = ?
        ''', (month,)).fetchone()['total']
        conn.close()
        return {
            'expenseStats': [dict(r) for r in expense_stats],
            'incomeTotal': income_total,
            'expenseTotal': expense_total
        }


# ============================================
# 编辑弹窗
# ============================================
class EditDialog(QDialog):
    def __init__(self, db, record, parent=None):
        super().__init__(parent)
        self.db = db
        self.record = record
        self.setWindowTitle("编辑记录")
        self.setFixedSize(440, 400)
        self.setStyleSheet(f"QDialog {{ background: {Colors.CARD_BG}; border-radius: 14px; }}")
        self.setGraphicsEffect(shadow(30, (0, 4), 15))

        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 28, 28, 28)

        # 金额
        self.amount_input = QLineEdit(str(record['amount']))
        layout.addRow(self._make_label("金额 (元)"), self.amount_input)

        # 类型
        self.type_input = QComboBox()
        self.type_input.addItem('支出', 'expense')
        self.type_input.addItem('收入', 'income')
        idx = self.type_input.findData(record['type'])
        if idx >= 0:
            self.type_input.setCurrentIndex(idx)
        self.type_input.currentTextChanged.connect(self._on_type_changed)
        layout.addRow(self._make_label("类型"), self.type_input)

        # 日期
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.fromString(record['date'], 'yyyy-MM-dd'))
        layout.addRow(self._make_label("日期"), self.date_input)

        # 分类
        self.category_input = QComboBox()
        layout.addRow(self._make_label("分类"), self.category_input)

        # 备注
        self.note_input = QLineEdit(record.get('note', ''))
        layout.addRow(self._make_label("备注"), self.note_input)

        self._load_categories()

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(self._outline_btn_css())
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet(self._primary_btn_css())
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addRow(btn_row)

    def _make_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_SECONDARY};")
        return lbl

    def _primary_btn_css(self):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0a04b, stop:1 {Colors.ACCENT});
                color: #fff;
                border: none;
                border-radius: 10px;
                padding: 11px 28px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5b55a, stop:1 {Colors.ACCENT_HOVER});
            }}
        """

    def _outline_btn_css(self):
        return f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1.5px solid {Colors.CARD_BORDER};
                border-radius: 10px;
                padding: 11px 28px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT};
                color: {Colors.ACCENT};
            }}
        """

    def _load_categories(self):
        cats = self.db.get_categories()
        rtype = self.type_input.currentData()
        filtered = [c for c in cats if c['name'] == '收入'] if rtype == 'income' else [c for c in cats if c['name'] != '收入']
        self.category_input.clear()
        for c in filtered:
            self.category_input.addItem(f"{c['icon']} {c['name']}", c['name'])
        idx = self.category_input.findData(self.record['category'])
        if idx >= 0:
            self.category_input.setCurrentIndex(idx)

    def _on_type_changed(self):
        self._load_categories()

    def _save(self):
        try:
            amount = float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效金额")
            return
        if amount <= 0:
            QMessageBox.warning(self, "错误", "金额必须大于0")
            return
        self.result_data = {
            'id': self.record['id'],
            'amount': amount,
            'type': self.type_input.currentData(),
            'category': self.category_input.currentData(),
            'subCategory': '',
            'note': self.note_input.text(),
            'date': self.date_input.date().toString('yyyy-MM-dd')
        }
        self.accept()


# ============================================
# 分类编辑弹窗
# ============================================
class CategoryEditDialog(QDialog):
    """编辑分类名称和图标的弹窗（仅限用户自建分类）"""

    def __init__(self, category, parent=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("编辑分类")
        self.setFixedSize(380, 220)
        self.setStyleSheet(f"QDialog {{ background: {Colors.CARD_BG}; border-radius: 14px; }}")
        self.setGraphicsEffect(shadow(30, (0, 4), 15))

        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 28, 28, 28)

        # 图标
        self.icon_input = QLineEdit(category['icon'])
        layout.addRow(self._make_label("图标"), self.icon_input)

        # 名称
        self.name_input = QLineEdit(category['name'])
        layout.addRow(self._make_label("分类名称"), self.name_input)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(self._outline_btn_css())
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet(self._primary_btn_css())
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addRow(btn_row)

    def _make_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {Colors.TEXT_SECONDARY};")
        return lbl

    def _primary_btn_css(self):
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0a04b, stop:1 {Colors.ACCENT});
                color: #fff;
                border: none;
                border-radius: 10px;
                padding: 11px 28px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5b55a, stop:1 {Colors.ACCENT_HOVER});
            }}
        """

    def _outline_btn_css(self):
        return f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1.5px solid {Colors.CARD_BORDER};
                border-radius: 10px;
                padding: 11px 28px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT};
                color: {Colors.ACCENT};
            }}
        """

    def _save(self):
        name = self.name_input.text().strip()
        icon = self.icon_input.text().strip() or '📌'
        if not name:
            QMessageBox.warning(self, "错误", "请输入分类名称")
            return
        self.result_data = {
            'id': self.category['id'],
            'name': name,
            'icon': icon
        }
        self.accept()


# ============================================
# 饼图画布
# ============================================
class PieChartCanvas(FigureCanvas):
    """Matplotlib 饼图，用于月度统计页面"""

    # 现代配色（12种柔和色彩）
    PALETTE = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#1abc9c',
               '#3498db', '#9b59b6', '#e91e63', '#00bcd4', '#ff6f00',
               '#8d6e63', '#607d8b']

    def __init__(self, parent=None):
        matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC']
        matplotlib.rcParams['axes.unicode_minus'] = False

        self.fig = Figure(figsize=(5.5, 4.2), facecolor='#ffffff')
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background: transparent;")

    def update_chart(self, stats):
        self.ax.clear()
        if not stats:
            self.ax.text(0.5, 0.5, '暂无数据\n添加记录后这里会出现饼图',
                         ha='center', va='center', fontsize=14, color='#b8a99a',
                         transform=self.ax.transAxes)
            self.ax.axis('off')
            self.fig.tight_layout(pad=2)
            self.draw()
            return

        labels = [s['category'] for s in stats]
        data = [s['total'] for s in stats]

        wedges, texts, autotexts = self.ax.pie(
            data, labels=None, autopct='%1.1f%%',
            colors=self.PALETTE[:len(labels)],
            startangle=90, pctdistance=0.58,
            wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
        )
        for t in autotexts:
            t.set_fontsize(9)
            t.set_fontweight('bold')
            t.set_color('#555')

        # 图例移到右侧
        self.ax.legend(
            wedges, labels,
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            fontsize=11,
            frameon=False,
            labelspacing=0.8
        )

        self.fig.tight_layout(pad=2)
        self.draw()


# ============================================
# 工具函数：创建带阴影的卡片容器
# ============================================
def make_card(parent=None):
    """
    创建一个白色圆角卡片，并附上柔和阴影。
    这是整个界面"现代感"的核心——让卡片从背景浮起来。
    """
    card = QWidget(parent)
    card.setStyleSheet(f"""
        QWidget {{
            background: {Colors.CARD_BG};
            border: 1px solid {Colors.CARD_BORDER};
            border-radius: 14px;
        }}
    """)
    card.setGraphicsEffect(shadow())
    return card


def make_page_title(text):
    """统一风格的页面标题"""
    title = QLabel(text)
    title.setStyleSheet(f"""
        font-size: 24px;
        font-weight: bold;
        color: {Colors.TEXT_PRIMARY};
        padding-bottom: 4px;
        letter-spacing: 0.5px;
    """)
    return title


def make_section_label(text):
    """统一风格的表单标签"""
    label = QLabel(text)
    label.setStyleSheet(f"""
        font-size: 14px;
        font-weight: bold;
        color: {Colors.TEXT_SECONDARY};
        margin-bottom: 2px;
    """)
    return label


# ============================================
# 主窗口
# ============================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("晚秋记账")
        self.setMinimumSize(1040, 680)
        self.resize(1140, 780)

        # 中央 widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- 侧边栏 ----
        self._build_sidebar(main_layout)

        # ---- 右侧内容区 ----
        self._build_content(main_layout)

        # 初始化
        self._load_categories_for_form()
        self._update_sidebar_summary()

    # ============================================
    # 侧边栏（重新设计 — 深色高级感）
    # ============================================
    def _build_sidebar(self, parent_layout):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background: {Colors.SIDEBAR_BG};")

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        # ---- 标题区域 ----
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(20, 24, 20, 18)

        # 橙色装饰点
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {Colors.ACCENT}; font-size: 12px; background: transparent;")
        title_layout.addWidget(dot)

        title = QLabel("晚秋记账")
        title.setStyleSheet(f"""
            color: {Colors.SIDEBAR_TEXT};
            font-size: 19px;
            font-weight: bold;
            background: transparent;
            letter-spacing: 1.5px;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()

        side_layout.addWidget(title_container)

        # ---- 分隔线 ----
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: rgba(255,255,255,0.06); max-height: 1px; margin: 0 16px;")
        side_layout.addWidget(sep)

        # ---- 导航按钮 ----
        nav_items = [
            ('add-record', '✏️', '记一笔'),
            ('records-list', '📋', '账单列表'),
            ('statistics', '📊', '月度统计'),
            ('categories', '🏷️', '分类管理'),
        ]
        self.nav_btns = {}
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(0)
        nav_layout.setContentsMargins(8, 12, 8, 12)

        for page_name, icon, label in nav_items:
            btn = QPushButton(f"  {icon}    {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # 使用对象名来标记页面
            btn.setObjectName(f"nav_{page_name}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.SIDEBAR_TEXT};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 6px;
                    padding: 13px 16px;
                    font-size: 15px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.05);
                }}
                QPushButton:checked {{
                    background: rgba(255,255,255,0.08);
                    color: #fff;
                    font-weight: bold;
                    border-left: 3px solid {Colors.ACCENT};
                }}
            """)
            btn.clicked.connect(lambda checked, p=page_name: self._switch_page(p))
            nav_layout.addWidget(btn)
            self.nav_btns[page_name] = btn

        side_layout.addWidget(nav_widget)

        # 弹簧（把底部推到最下）
        side_layout.addStretch()

        # ---- 底部当月汇总 ----
        footer_sep = QFrame()
        footer_sep.setFrameShape(QFrame.Shape.HLine)
        footer_sep.setStyleSheet("background: rgba(255,255,255,0.06); max-height: 1px;")
        side_layout.addWidget(footer_sep)

        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 16, 20, 22)
        footer_layout.setSpacing(6)

        summary_icon = QLabel("💰 当月支出")
        summary_icon.setStyleSheet(f"""
            color: {Colors.SIDEBAR_TEXT_MUTED};
            font-size: 12px;
            background: transparent;
            letter-spacing: 0.3px;
        """)
        footer_layout.addWidget(summary_icon)

        self.summary_amount = QLabel("¥ 0.00")
        self.summary_amount.setStyleSheet(f"""
            color: {Colors.ACCENT};
            font-size: 24px;
            font-weight: bold;
            background: transparent;
        """)
        footer_layout.addWidget(self.summary_amount)

        side_layout.addWidget(footer)
        parent_layout.addWidget(sidebar)

        # 默认选中第一个
        self.nav_btns['add-record'].setChecked(True)

    # ============================================
    # 内容区（4个页面）
    # ============================================
    def _build_content(self, parent_layout):
        content = QWidget()
        content.setStyleSheet(f"background: {Colors.PAGE_BG};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 32, 36, 32)

        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background: transparent;")
        self.pages.addWidget(self._build_add_record_page())
        self.pages.addWidget(self._build_records_list_page())
        self.pages.addWidget(self._build_statistics_page())
        self.pages.addWidget(self._build_categories_page())
        content_layout.addWidget(self.pages)

        parent_layout.addWidget(content, 1)

    def _switch_page(self, page_name):
        for btn in self.nav_btns.values():
            btn.setChecked(False)
        self.nav_btns[page_name].setChecked(True)

        page_map = {'add-record': 0, 'records-list': 1, 'statistics': 2, 'categories': 3}
        self.pages.setCurrentIndex(page_map[page_name])

        if page_name == 'records-list':
            self._load_records()
        elif page_name == 'statistics':
            self._load_statistics()
        elif page_name == 'categories':
            self._load_categories()
        elif page_name == 'add-record':
            self._load_categories_for_form()

    # ============================================
    # 页面1：记一笔（卡片 + 阴影 + 渐变按钮）
    # ============================================
    def _build_add_record_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        layout.addWidget(make_page_title("✏️  记一笔"))
        layout.addSpacing(4)

        # 表单卡片
        card = make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(18)

        # 金额
        amt_layout = QVBoxLayout()
        amt_layout.setSpacing(6)
        amt_layout.addWidget(make_section_label("金额 (元)"))
        self.record_amount = QLineEdit()
        self.record_amount.setPlaceholderText("输入消费金额，例如：32.50")
        self.record_amount.setMinimumHeight(44)
        amt_layout.addWidget(self.record_amount)
        card_layout.addLayout(amt_layout)

        # 类型 + 分类 同行
        row1 = QHBoxLayout()
        row1.setSpacing(24)

        type_layout = QVBoxLayout()
        type_layout.setSpacing(6)
        type_layout.addWidget(make_section_label("类型"))
        self.record_type = QComboBox()
        self.record_type.addItem('支出', 'expense')
        self.record_type.addItem('收入', 'income')
        self.record_type.setMinimumHeight(44)
        self.record_type.currentTextChanged.connect(self._load_categories_for_form)
        type_layout.addWidget(self.record_type)
        row1.addLayout(type_layout)

        cat_layout = QVBoxLayout()
        cat_layout.setSpacing(6)
        cat_layout.addWidget(make_section_label("分类"))
        self.record_category = QComboBox()
        self.record_category.setMinimumHeight(44)
        cat_layout.addWidget(self.record_category)
        row1.addLayout(cat_layout)

        card_layout.addLayout(row1)

        # 日期 + 备注 同行
        row2 = QHBoxLayout()
        row2.setSpacing(24)

        date_layout = QVBoxLayout()
        date_layout.setSpacing(6)
        date_layout.addWidget(make_section_label("日期"))
        self.record_date = QDateEdit()
        self.record_date.setCalendarPopup(True)
        self.record_date.setDate(QDate.currentDate())
        self.record_date.setMinimumHeight(44)
        date_layout.addWidget(self.record_date)
        row2.addLayout(date_layout)

        note_layout = QVBoxLayout()
        note_layout.setSpacing(6)
        note_layout.addWidget(make_section_label("备注 (可选)"))
        self.record_note = QLineEdit()
        self.record_note.setPlaceholderText("例如：午餐外卖")
        self.record_note.setMinimumHeight(44)
        note_layout.addWidget(self.record_note)
        row2.addLayout(note_layout)

        card_layout.addLayout(row2)

        # 提交按钮（渐变 + 阴影）
        card_layout.addSpacing(6)
        submit_btn = QPushButton("保存记录")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setMinimumHeight(48)
        submit_btn.setFixedWidth(160)
        submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0a04b, stop:1 {Colors.ACCENT});
                color: #fff;
                border: none;
                border-radius: 12px;
                padding: 12px 32px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5b55a, stop:1 {Colors.ACCENT_HOVER});
            }}
            QPushButton:pressed {{
                background: {Colors.ACCENT_HOVER};
            }}
        """)
        submit_btn.setGraphicsEffect(shadow(15, (0, 3), 20))
        submit_btn.clicked.connect(self._submit_record)
        card_layout.addWidget(submit_btn)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _load_categories_for_form(self):
        cats = self.db.get_categories()
        rtype = self.record_type.currentData()
        filtered = [c for c in cats if c['name'] == '收入'] if rtype == 'income' else [c for c in cats if c['name'] != '收入']
        self.record_category.clear()
        self.record_category.addItem("请选择分类", None)
        for c in filtered:
            self.record_category.addItem(f"{c['icon']}  {c['name']}", c['name'])

    def _submit_record(self):
        try:
            amount = float(self.record_amount.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的金额")
            return
        if amount <= 0:
            QMessageBox.warning(self, "错误", "金额必须大于0")
            return

        category = self.record_category.currentData()
        if not category:
            QMessageBox.warning(self, "错误", "请选择分类")
            return

        self.db.add_record(
            amount=amount,
            rtype=self.record_type.currentData(),
            category=category,
            sub_category='',
            note=self.record_note.text().strip(),
            date=self.record_date.date().toString('yyyy-MM-dd')
        )

        self.record_amount.clear()
        self.record_note.clear()
        self.record_category.setCurrentIndex(0)
        self.record_date.setDate(QDate.currentDate())
        self._update_sidebar_summary()
        QMessageBox.information(self, "成功", "✅ 记录保存成功！")

    # ============================================
    # 页面2：账单列表（表格式样优化）
    # ============================================
    def _build_records_list_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setSpacing(18)

        layout.addWidget(make_page_title("📋  账单列表"))

        # 筛选栏卡片
        filter_card = make_card()
        filter_card_layout = QHBoxLayout(filter_card)
        filter_card_layout.setContentsMargins(20, 10, 20, 10)
        filter_card_layout.setSpacing(12)

        month_label = QLabel("筛选月份")
        month_label.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        filter_card_layout.addWidget(month_label)

        self.filter_month = QComboBox()
        self.filter_month.setMinimumWidth(130)
        self.filter_month.setMinimumHeight(38)
        now = QDate.currentDate()
        for y in range(now.year(), now.year() - 3, -1):
            for m in range(12, 0, -1):
                date = QDate(y, m, 1)
                if date <= now or (y == now.year() and m <= now.month()):
                    self.filter_month.addItem(date.toString('yyyy-MM'), date.toString('yyyy-MM'))
        self.filter_month.addItem("全部", None)
        self.filter_month.currentTextChanged.connect(self._load_records)
        filter_card_layout.addWidget(self.filter_month)

        clear_btn = QPushButton("清除筛选")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1.5px solid {Colors.CARD_BORDER};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT};
                color: {Colors.ACCENT};
            }}
        """)
        clear_btn.clicked.connect(lambda: self.filter_month.setCurrentText("全部"))
        filter_card_layout.addWidget(clear_btn)

        filter_card_layout.addStretch()
        layout.addWidget(filter_card)

        # 表格
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(['日期', '类型', '分类', '金额', '备注', '操作'])
        self.records_table.horizontalHeader().setStretchLastSection(True)
        self.records_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.records_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.setShowGrid(False)
        self.records_table.verticalHeader().setVisible(False)
        self.records_table.setGraphicsEffect(shadow())
        # 交替行颜色通过 palette 设置
        self.records_table.setStyleSheet(f"""
            QTableWidget {{
                background: {Colors.CARD_BG};
                border: 1px solid {Colors.CARD_BORDER};
                border-radius: 14px;
                gridline-color: transparent;
            }}
            QTableWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid #f5f0e9;
                font-size: 14px;
            }}
            QTableWidget::item:alternate {{
                background: #fdf9f3;
            }}
            QHeaderView::section {{
                background: #fdf9f3;
                color: {Colors.TEXT_SECONDARY};
                font-size: 13px;
                font-weight: bold;
                padding: 14px 16px;
                border: none;
                border-bottom: 2px solid {Colors.CARD_BORDER};
                letter-spacing: 0.3px;
            }}
        """)
        layout.addWidget(self.records_table)

        return page

    def _load_records(self):
        month = self.filter_month.currentData()
        records = self.db.get_records(month)

        self.records_table.setRowCount(len(records))
        for i, r in enumerate(records):
            # 日期
            self.records_table.setItem(i, 0, QTableWidgetItem(r['date']))

            # 类型
            type_text = '支出' if r['type'] == 'expense' else '收入'
            type_item = QTableWidgetItem(type_text)
            type_item.setForeground(QColor(Colors.DANGER) if r['type'] == 'expense' else QColor(Colors.SUCCESS))
            self.records_table.setItem(i, 1, type_item)

            # 分类
            self.records_table.setItem(i, 2, QTableWidgetItem(r['category']))

            # 金额
            sign = '-' if r['type'] == 'expense' else '+'
            amount_text = f"{sign}¥ {abs(r['amount']):,.2f}"
            amt_item = QTableWidgetItem(amount_text)
            amt_item.setForeground(QColor(Colors.DANGER) if r['type'] == 'expense' else QColor(Colors.SUCCESS))
            self.records_table.setItem(i, 3, amt_item)

            # 备注
            self.records_table.setItem(i, 4, QTableWidgetItem(r['note'] or '-'))

            # 操作按钮
            btn_widget = QWidget()
            btn_widget.setStyleSheet("background: transparent;")
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(8)

            edit_btn = QPushButton("编辑")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border: 1.5px solid {Colors.CARD_BORDER};
                    border-radius: 6px;
                    padding: 5px 14px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    border-color: {Colors.ACCENT};
                    color: {Colors.ACCENT};
                    background: {Colors.ACCENT_LIGHT};
                }}
            """)
            edit_btn.clicked.connect(lambda checked, rid=r['id']: self._edit_record(rid))
            btn_layout.addWidget(edit_btn)

            del_btn = QPushButton("删除")
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.DANGER};
                    border: 1px solid {Colors.DANGER};
                    border-radius: 6px;
                    padding: 5px 14px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {Colors.DANGER};
                    color: #fff;
                }}
            """)
            del_btn.clicked.connect(lambda checked, rid=r['id']: self._delete_record(rid))
            btn_layout.addWidget(del_btn)

            self.records_table.setCellWidget(i, 5, btn_widget)
            self.records_table.setRowHeight(i, 52)

    def _edit_record(self, rec_id):
        records = self.db.get_records()
        record = next((r for r in records if r['id'] == rec_id), None)
        if not record:
            return
        dlg = EditDialog(self.db, record, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.result_data
            self.db.update_record(
                data['id'], data['amount'], data['type'],
                data['category'], data['subCategory'], data['note'], data['date']
            )
            self._load_records()
            self._update_sidebar_summary()

    def _delete_record(self, rec_id):
        reply = QMessageBox.question(self, "确认删除", "确定要删除这条记录吗？此操作不可撤销。",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_record(rec_id)
            self._load_records()
            self._update_sidebar_summary()

    # ============================================
    # 页面3：月度统计（卡片优化 + 现代饼图配色）
    # ============================================
    def _build_statistics_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setSpacing(18)

        layout.addWidget(make_page_title("📊  月度统计"))

        # 月份选择卡片
        month_card = make_card()
        month_card_layout = QHBoxLayout(month_card)
        month_card_layout.setContentsMargins(20, 10, 20, 10)
        month_card_layout.setSpacing(12)

        month_label = QLabel("选择月份")
        month_label.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        month_card_layout.addWidget(month_label)

        self.stats_month = QComboBox()
        self.stats_month.setMinimumWidth(130)
        self.stats_month.setMinimumHeight(38)
        now = QDate.currentDate()
        for y in range(now.year(), now.year() - 3, -1):
            for m in range(12, 0, -1):
                date = QDate(y, m, 1)
                if date <= now or (y == now.year() and m <= now.month()):
                    self.stats_month.addItem(date.toString('yyyy-MM'), date.toString('yyyy-MM'))
        self.stats_month.currentTextChanged.connect(self._load_statistics)
        month_card_layout.addWidget(self.stats_month)
        month_card_layout.addStretch()
        layout.addWidget(month_card)

        # 三个统计卡片
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        # 支出卡片
        self.expense_card = self._make_stat_card("支出合计", "#e74c3c")
        self.expense_value = self._stat_card_value("#e74c3c")
        self.expense_card.layout().addWidget(self.expense_value)
        cards_row.addWidget(self.expense_card)

        # 收入卡片
        self.income_card = self._make_stat_card("收入合计", "#27ae60")
        self.income_value = self._stat_card_value("#27ae60")
        self.income_card.layout().addWidget(self.income_value)
        cards_row.addWidget(self.income_card)

        # 结余卡片
        self.balance_card = self._make_stat_card("月度结余", "#e67e22")
        self.balance_value = self._stat_card_value("#e67e22")
        self.balance_card.layout().addWidget(self.balance_value)
        cards_row.addWidget(self.balance_card)

        layout.addLayout(cards_row)

        # 饼图卡片
        chart_card = make_card()
        chart_card_layout = QVBoxLayout(chart_card)
        chart_card_layout.setContentsMargins(20, 20, 20, 20)
        chart_title = QLabel("支出分类占比")
        chart_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        chart_card_layout.addWidget(chart_title)
        self.pie_chart = PieChartCanvas()
        chart_card_layout.addWidget(self.pie_chart)
        layout.addWidget(chart_card, 1)

        return page

    def _make_stat_card(self, title, accent_color):
        """创建统计卡片：白色圆角 + 彩色圆点 + 阴影"""
        card = make_card()
        card.setGraphicsEffect(shadow(16, (0, 2), 6))

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(10)

        # 标题行：彩色圆点 + 文字
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setContentsMargins(0, 0, 0, 0)

        dot = QLabel("●")
        dot.setStyleSheet(f"font-size: 8px; color: {accent_color}; background: transparent;")
        dot.setFixedWidth(12)
        title_row.addWidget(dot)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        title_row.addWidget(title_label)
        title_row.addStretch()

        card_layout.addLayout(title_row)

        return card

    def _stat_card_value(self, color):
        lbl = QLabel("¥ 0.00")
        lbl.setStyleSheet(f"""
            font-size: 26px;
            font-weight: 600;
            color: {color};
            background: transparent;
            padding-left: 2px;
        """)
        return lbl

    def _load_statistics(self):
        month = self.stats_month.currentText()
        stats = self.db.get_monthly_stats(month)
        self.expense_value.setText(f"¥ {stats['expenseTotal']:,.2f}")
        self.income_value.setText(f"¥ {stats['incomeTotal']:,.2f}")
        balance = stats['incomeTotal'] - stats['expenseTotal']
        self.balance_value.setText(f"¥ {balance:,.2f}")
        self.pie_chart.update_chart(stats['expenseStats'])

    # ============================================
    # 页面4：分类管理（网格卡片优化）
    # ============================================
    def _build_categories_page(self):
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setSpacing(18)

        layout.addWidget(make_page_title("🏷️  分类管理"))

        # 添加分类表单卡片
        add_card = make_card()
        add_card_layout = QHBoxLayout(add_card)
        add_card_layout.setContentsMargins(20, 16, 20, 16)
        add_card_layout.setSpacing(12)

        icon_label = QLabel("图标")
        icon_label.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        add_card_layout.addWidget(icon_label)

        self.new_cat_icon = QLineEdit("📌")
        self.new_cat_icon.setMaximumWidth(56)
        self.new_cat_icon.setMinimumHeight(44)
        self.new_cat_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        add_card_layout.addWidget(self.new_cat_icon)

        name_label = QLabel("名称")
        name_label.setStyleSheet(f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        add_card_layout.addWidget(name_label)

        self.new_cat_name = QLineEdit()
        self.new_cat_name.setPlaceholderText("输入分类名称，如：宠物")
        self.new_cat_name.setMaximumWidth(220)
        self.new_cat_name.setMinimumHeight(44)
        add_card_layout.addWidget(self.new_cat_name)

        add_btn = QPushButton("添加分类")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setMinimumHeight(44)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0a04b, stop:1 {Colors.ACCENT});
                color: #fff;
                border: none;
                border-radius: 10px;
                padding: 10px 22px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5b55a, stop:1 {Colors.ACCENT_HOVER});
            }}
        """)
        add_btn.clicked.connect(self._add_category)
        add_card_layout.addWidget(add_btn)
        add_card_layout.addStretch()

        layout.addWidget(add_card)

        # 分类网格容器（使用滚动区域 + 网格）
        grid_card = make_card()
        grid_card_inner = QVBoxLayout(grid_card)
        grid_card_inner.setContentsMargins(20, 20, 20, 20)

        self.categories_grid = QGridLayout()
        self.categories_grid.setSpacing(12)
        grid_card_inner.addLayout(self.categories_grid)
        grid_card_inner.addStretch()

        layout.addWidget(grid_card, 1)
        return page

    def _load_categories(self):
        # 清除旧网格
        while self.categories_grid.count():
            item = self.categories_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cats = self.db.get_categories()
        cols = 4
        for i, c in enumerate(cats):
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background: #fdf9f3;
                    border: 1px solid {Colors.CARD_BORDER};
                    border-radius: 10px;
                }}
            """)
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            card_layout.setSpacing(10)

            icon_label = QLabel(c['icon'])
            icon_label.setStyleSheet("font-size: 24px; background: transparent;")
            card_layout.addWidget(icon_label)

            name_label = QLabel(c['name'])
            name_label.setStyleSheet(f"font-size: 15px; font-weight: 500; color: {Colors.TEXT_PRIMARY}; background: transparent;")
            card_layout.addWidget(name_label)

            if c['is_default']:
                card_layout.addStretch()
                badge = QLabel("默认")
                badge.setStyleSheet(f"""
                    font-size: 11px;
                    color: {Colors.TEXT_MUTED};
                    background: #f5efe6;
                    padding: 3px 10px;
                    border-radius: 10px;
                """)
                card_layout.addWidget(badge)
            else:
                card_layout.addStretch()
                edit_btn = QPushButton("✎")
                edit_btn.setFixedSize(28, 28)
                edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                edit_btn.setToolTip("编辑分类")
                edit_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: none;
                        border: none;
                        color: #ccc;
                        font-size: 15px;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        color: {Colors.ACCENT};
                        background: {Colors.ACCENT_LIGHT};
                    }}
                """)
                edit_btn.clicked.connect(lambda checked, c=dict(c): self._edit_category(c))
                card_layout.addWidget(edit_btn)

                del_btn = QPushButton("✕")
                del_btn.setFixedSize(28, 28)
                del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                del_btn.setToolTip("删除分类")
                del_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: none;
                        border: none;
                        color: #ccc;
                        font-size: 16px;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        color: {Colors.DANGER};
                        background: #fde8e8;
                    }}
                """)
                del_btn.clicked.connect(lambda checked, cid=c['id'], cname=c['name']: self._delete_category(cid, cname))
                card_layout.addWidget(del_btn)

            row, col = i // cols, i % cols
            self.categories_grid.addWidget(card, row, col)

    def _add_category(self):
        name = self.new_cat_name.text().strip()
        icon = self.new_cat_icon.text().strip() or '📌'
        if not name:
            QMessageBox.warning(self, "错误", "请输入分类名称")
            return
        try:
            self.db.add_category(name, icon)
            self.new_cat_name.clear()
            self.new_cat_icon.setText('📌')
            self._load_categories()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "错误", "添加失败，分类名称可能已存在")

    def _delete_category(self, cat_id, cat_name):
        reply = QMessageBox.question(self, "确认删除", f"确定要删除分类「{cat_name}」吗？")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_category(cat_id)
            self._load_categories()

    def _edit_category(self, category):
        """打开编辑弹窗修改分类名称和图标"""
        dlg = CategoryEditDialog(category, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.result_data
            try:
                self.db.update_category(data['id'], data['name'], data['icon'])
                self._load_categories()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "错误", "修改失败，分类名称可能已存在")

    # ============================================
    # 侧边栏月度汇总
    # ============================================
    def _update_sidebar_summary(self):
        month = QDate.currentDate().toString('yyyy-MM')
        stats = self.db.get_monthly_stats(month)
        self.summary_amount.setText(f"¥ {stats['expenseTotal']:,.2f}")


# ============================================
# 启动
# ============================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # 全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 全局样式表 — 这是整个应用"变好看"的核心，
    # 相当于给所有控件统一穿上一套"衣服"
    app.setStyleSheet(GLOBAL_QSS)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
