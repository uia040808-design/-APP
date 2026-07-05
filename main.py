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
    QSizePolicy, QSpacerItem, QGraphicsDropShadowEffect, QToolButton, QStyle, QMenu
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer, QRectF
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction, QPainter, QPen, QBrush, QKeyEvent

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
# 注：QSS（Qt Style Sheets）是 PyQt 中的样式语言，功能类似网页的 CSS。
# 通俗理解：下面这段代码就像给整个应用的"穿衣打扮"，统一设置所有控件的外观。
GLOBAL_QSS = f"""
/* === 全局基础 === */
/* 设置主窗口和所有控件的默认字体、字号、文字颜色 */
QMainWindow {{
    background-color: {Colors.PAGE_BG};
}}

QWidget {{
    font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 15px;
    color: {Colors.TEXT_PRIMARY};
}}

/* === 全局输入框 === */
/* 统一所有输入类控件的外观：圆角边框、内边距、聚焦时高亮 */
/* 注：selection-background-color 是用户选中文字时的背景色 */
QLineEdit, QComboBox, QDateEdit, QTextEdit {{
    padding: 12px 14px;
    border: 1.5px solid {Colors.INPUT_BORDER};
    border-radius: 10px;
    background: #ffffff;
    font-size: 16px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_LIGHT};
}}

/* 输入框获得焦点（点击进入）时，边框变为橙色，提示用户"正在这里输入" */
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border-color: {Colors.ACCENT};
}}

/* === 下拉框 === */
/* 下拉框右侧的箭头按钮区域：去掉默认边框，只保留箭头图标 */
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 36px;
    border: none;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    background: transparent;
}}

QComboBox::down-arrow {{
    width: 14px;
    height: 14px;
}}

/* 下拉框展开后的选项列表：圆角白色背景，悬停项用浅橙色高亮 */
QComboBox QAbstractItemView {{
    background: #fff;
    border: 1px solid {Colors.CARD_BORDER};
    border-radius: 10px;
    padding: 8px;
    font-size: 16px;
    selection-background-color: {Colors.ACCENT_LIGHT};
    selection-color: {Colors.TEXT_PRIMARY};
    outline: none;
}}

/* 下拉列表中每个选项的内边距和圆角 */
QComboBox QAbstractItemView::item {{
    padding: 10px 14px;
    border-radius: 8px;
    min-height: 32px;
}}

/* === 日期编辑框的下拉按钮 === */
/* 日期选择框右侧的日历图标按钮，样式和下拉框保持一致 */
QDateEdit::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 36px;
    border: none;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    background: transparent;
}}

/* === 滚动条 === */
/* 垂直滚动条：细窄设计（8px宽），咖啡色滑块，悬停时加深 */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}

/* 注：handle 就是滚动条上可拖动的"小方块" */
QScrollBar::handle:vertical {{
    background: #d4c5b2;
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: #b8a08a;
}}

/* 隐藏滚动条两端的箭头按钮（add-line/sub-line），让外观更简洁 */
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* 滚动条轨道（滑块之外的区域）设为透明 */
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

/* 水平滚动条：和垂直滚动条风格一致 */
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
/* 账单列表表格：白色背景、圆角、无网格线，选中行用浅橙色高亮 */
QTableWidget {{
    background: #ffffff;
    border: 1px solid {Colors.CARD_BORDER};
    border-radius: 12px;
    gridline-color: transparent;
    selection-background-color: {Colors.ACCENT_LIGHT};
    selection-color: {Colors.TEXT_PRIMARY};
}}

/* 表格每个单元格的内边距和底部分隔线 */
QTableWidget::item {{
    padding: 10px 14px;
    border-bottom: 1px solid #f5f0e9;
}}

/* 表头：浅米色背景、深色粗体文字、底部有加粗分隔线 */
QHeaderView::section {{
    background: #fdf9f3;
    color: {Colors.TEXT_SECONDARY};
    font-size: 14px;
    font-weight: bold;
    padding: 14px;
    border: none;
    border-bottom: 2px solid {Colors.CARD_BORDER};
    letter-spacing: 0.3px;
}}

/* === 消息框 === */
/* 弹窗提示框的样式 */
QMessageBox {{
    background: #ffffff;
}}

QMessageBox QPushButton {{
    padding: 8px 20px;
    border-radius: 8px;
    font-size: 15px;
    min-width: 80px;
}}
"""


# ============================================
# 数据库管理（完全不变）
# ============================================
class Database:
    """
    数据库管理类——负责所有记账数据的存取。
    通俗理解：这是应用的"账本大管家"，所有和存钱、查账、分类有关的操作都通过它来完成。

    注：数据存储在 Windows 用户目录下的 AppData\\Roaming\\晚秋记账\\data.db 文件中，
    这个位置是 Windows 的标准应用数据目录，不会丢失，也不会被误删。
    """

    def __init__(self):
        """
        初始化数据库连接。
        自动创建存储目录和数据库文件（如果还不存在的话），
        然后建表和写入预设分类。
        """
        # APPDATA 是 Windows 系统变量，指向当前用户的应用程序数据目录
        # 例如：C:\Users\你的用户名\AppData\Roaming
        appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
        db_dir = os.path.join(appdata, '晚秋记账')
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, 'data.db')
        self.init_db()

    def get_conn(self):
        """
        获取数据库连接。
        通俗理解：拿起电话，拨通数据库的号码，建立一条通话线路。
        每次查/改数据前都需要先"打通电话"。

        注：WAL 模式（Write-Ahead Logging）让读写可以同时进行，不会互相卡住。
        类比：就像写日记时，新内容先写在便签上，等有空再抄到日记本里，
        这样想读日记的人不需要等你写完。
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 让查询结果可以用字段名访问，例如 row['name']
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def init_db(self):
        """
        初始化数据库——建表和写入预设分类。
        注：只在首次运行（数据库文件不存在或分类表为空）时执行。
        以后每次启动应用，这部分会自动跳过。
        """
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
        """
        获取所有分类。
        通俗理解：翻开"分类目录"页，看看有哪些花钱/收入的类别。
        返回一个列表，每个元素是一个字典，包含 id、name、icon、is_default 字段。
        """
        conn = self.get_conn()
        rows = conn.execute('SELECT * FROM categories ORDER BY id').fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_category(self, name, icon):
        """
        新增一个自定义分类。
        通俗理解：在"分类目录"里添加一个新类别（比如"宠物"），
        以后记一笔时就可以选它了。
        注：预设分类（is_default=1）不能新增，只有用户自定义的才行。
        """
        conn = self.get_conn()
        cur = conn.execute('INSERT INTO categories (name, icon) VALUES (?, ?)', (name, icon))
        conn.commit()
        cat_id = cur.lastrowid
        conn.close()
        return {'id': cat_id, 'name': name, 'icon': icon}

    def delete_category(self, cat_id):
        """
        删除自定义分类（预设分类不可删除）。
        注：SQL 中的 is_default = 0 条件保护了预设分类，
        即使用户在界面上看不到删除按钮，数据库层也做了二次保护。
        """
        conn = self.get_conn()
        conn.execute('DELETE FROM categories WHERE id = ? AND is_default = 0', (cat_id,))
        conn.commit()
        conn.close()

    def update_category(self, cat_id, name, icon):
        """
        更新分类名称和图标（仅限非预置分类）。
        通俗理解：给自建分类改名或换个图标，预设分类不允许修改。
        """
        conn = self.get_conn()
        conn.execute(
            'UPDATE categories SET name = ?, icon = ? WHERE id = ? AND is_default = 0',
            (name, icon, cat_id)
        )
        conn.commit()
        conn.close()

    def add_record(self, amount, rtype, category, sub_category, note, date):
        """
        新增一条记账记录。
        参数说明：
        - amount: 金额（正数），如 32.50
        - rtype: 类型，'expense'（支出）或 'income'（收入）
        - category: 分类名称，如 '餐饮'
        - sub_category: 子分类（目前预留，可留空）
        - note: 备注，如 '午餐外卖'
        - date: 日期，格式 'YYYY-MM-DD'，如 '2024-07-05'
        注：所有参数使用 ? 占位符传给 SQL，防止 SQL 注入攻击。
        """
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
        """
        更新一条已有的记账记录。
        通俗理解：如果之前记错了金额或选错了分类，用这个方法修改。
        参数含义和 add_record 一致。
        """
        conn = self.get_conn()
        conn.execute(
            'UPDATE records SET amount=?, type=?, category=?, sub_category=?, note=?, date=? WHERE id=?',
            (amount, rtype, category, sub_category or '', note or '', date, rec_id)
        )
        conn.commit()
        conn.close()

    def delete_record(self, rec_id):
        """
        删除一条记账记录（不可撤销）。
        注：删除前会弹出确认框，防止误删。
        """
        conn = self.get_conn()
        conn.execute('DELETE FROM records WHERE id = ?', (rec_id,))
        conn.commit()
        conn.close()

    def get_records(self, month=None):
        """
        查询账单记录。
        通俗理解：翻开"记账本"，可以看全部记录，也可以只看某个月份的。
        参数：
        - month: 可选，格式 'YYYY-MM'（如 '2024-07'），传 None 则返回全部记录。
        排序：最新日期排最前面，同日期按 ID 倒序（后录入的先显示）。
        """
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
        """
        获取某个月的统计汇总数据。
        通俗理解：算出这个月一共花了多少、赚了多少、每个分类各花了多少。
        返回值是一个字典：
        - expenseStats: 各分类支出金额列表（从高到低排序）
        - incomeTotal: 本月收入合计
        - expenseTotal: 本月支出合计

        注：COALESCE(SUM(amount), 0) 的意思是"如果这个月没有数据，就返回 0 而不是空"，
        防止界面显示报错。
        """
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
    """
    编辑记录弹窗 — 在账单列表中右键点击"编辑"后弹出。
    通俗理解：一个"修改账单"的小窗口，可以改金额、分类、日期等信息。
    和记一笔的界面类似，但预先填好了已有数据。
    """

    def __init__(self, db, record, parent=None):
        super().__init__(parent)
        self.db = db
        self.record = record  # 当前要编辑的那条记录的数据
        self.setWindowTitle("编辑记录")
        self.setFixedSize(440, 400)
        self.setStyleSheet(f"QDialog {{ background: {Colors.CARD_BG}; border-radius: 14px; }}")
        self.setGraphicsEffect(shadow(30, (0, 4), 15))

        # 注：QFormLayout 是 PyQt 的表单布局，自动生成"标签-输入框"成对排列的效果
        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 28, 28, 28)

        # 金额 — 预填当前记录的金额值
        self.amount_input = QLineEdit(str(record['amount']))
        layout.addRow(self._make_label("金额 (元)"), self.amount_input)

        # 类型 — 下拉选择"支出"或"收入"
        self.type_input = QComboBox()
        self.type_input.addItem('支出', 'expense')
        self.type_input.addItem('收入', 'income')
        idx = self.type_input.findData(record['type'])
        if idx >= 0:
            self.type_input.setCurrentIndex(idx)
        self.type_input.currentTextChanged.connect(self._on_type_changed)
        layout.addRow(self._make_label("类型"), self.type_input)

        # 日期 — 使用日期选择器，预填记录的日期
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.fromString(record['date'], 'yyyy-MM-dd'))
        layout.addRow(self._make_label("日期"), self.date_input)

        # 分类 — 下拉列表，根据选择的类型动态过滤
        self.category_input = QComboBox()
        layout.addRow(self._make_label("分类"), self.category_input)

        # 备注 — 预填原有备注
        self.note_input = QLineEdit(record.get('note', ''))
        layout.addRow(self._make_label("备注"), self.note_input)

        self._load_categories()

        # 按钮行：取消（灰色边框）+ 保存（橙色渐变）
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(self._outline_btn_css())
        cancel_btn.clicked.connect(self.reject)  # reject() 关闭弹窗并返回"拒绝"状态
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet(self._primary_btn_css())
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addRow(btn_row)

    def _make_label(self, text):
        """创建统一风格的表单项标签（粗体、次要文字色）"""
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {Colors.TEXT_SECONDARY};")
        return lbl

    def _primary_btn_css(self):
        """主按钮样式（橙色渐变、白色文字、圆角）—— 用于"保存"按钮"""
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
        """次要按钮样式（透明背景、灰色边框、悬停变橙色）—— 用于"取消"按钮"""
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
        """
        加载分类列表到下拉框。
        根据当前选择的类型（支出/收入）过滤分类：
        - 选择"收入"时，只显示"收入"分类
        - 选择"支出"时，显示除"收入"外的所有分类
        这样用户不会在收入里选到"餐饮"，也不会在支出里选到"收入"。
        """
        cats = self.db.get_categories()
        rtype = self.type_input.currentData()
        filtered = [c for c in cats if c['name'] == '收入'] if rtype == 'income' else [c for c in cats if c['name'] != '收入']
        self.category_input.clear()
        for c in filtered:
            self.category_input.addItem(f"{c['icon']} {c['name']}", c['name'])
        # 尝试恢复之前选中的分类
        idx = self.category_input.findData(self.record['category'])
        if idx >= 0:
            self.category_input.setCurrentIndex(idx)

    def _on_type_changed(self):
        """当类型下拉框切换时（支出↔收入），重新加载对应的分类列表"""
        self._load_categories()

    def _save(self):
        """
        校验并保存编辑结果。
        校验规则：
        1. 金额必须是有效数字
        2. 金额必须大于 0
        校验通过后，把填好的数据打包到 self.result_data，然后关闭弹窗。
        注：self.accept() 关闭弹窗并返回"接受"状态，外部调用方据此判断是否保存成功。
        """
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
    """
    编辑分类弹窗 — 在分类管理页面点击编辑按钮后弹出。
    通俗理解：给自建分类改个名字或换个图标的小窗口。
    注：预设分类（is_default=1）没有编辑按钮，永远不会弹出这个窗口。
    """

    def __init__(self, category, parent=None):
        super().__init__(parent)
        self.category = category  # 当前要编辑的分类信息
        self.setWindowTitle("编辑分类")
        self.setFixedSize(380, 220)
        self.setStyleSheet(f"QDialog {{ background: {Colors.CARD_BG}; border-radius: 14px; }}")
        self.setGraphicsEffect(shadow(30, (0, 4), 15))

        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 28, 28, 28)

        # 图标 — 预填当前图标
        self.icon_input = QLineEdit(category['icon'])
        layout.addRow(self._make_label("图标"), self.icon_input)

        # 名称 — 预填当前名称
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
        """创建统一风格的表单项标签"""
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {Colors.TEXT_SECONDARY};")
        return lbl

    def _primary_btn_css(self):
        """主按钮样式（橙色渐变）"""
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
        """次要按钮样式（灰色边框）"""
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
        """
        校验并保存分类编辑。
        规则：
        - 名称不能为空
        - 图标如果留空，默认使用 📌
        校验通过后，打包数据到 self.result_data 并关闭弹窗。
        """
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
    """
    Matplotlib 饼图画布 — 用于月度统计页面展示"各分类支出占比"。
    通俗理解：这就是统计页上的那个圆形图表，每一块扇形代表一个分类，
    扇形越大 = 这个月在这个分类上花的钱越多。

    注：FigureCanvas 是 Matplotlib 提供的 PyQt 兼容画布，
    让 Matplotlib 的图表能嵌入到 PyQt 窗口中显示。
    """

    # 现代配色（12种柔和色彩），分配给不同的分类
    PALETTE = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#1abc9c',
               '#3498db', '#9b59b6', '#e91e63', '#00bcd4', '#ff6f00',
               '#8d6e63', '#607d8b']

    def __init__(self, parent=None):
        # 设置中文字体，防止饼图中的中文变成方块（□）
        # 注：sans-serif 是无衬线字体（没有装饰线的字体），中文显示更清晰
        matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC']
        matplotlib.rcParams['axes.unicode_minus'] = False  # 让负号正常显示，不被当成乱码

        self.fig = Figure(figsize=(5.5, 4.2), facecolor='#ffffff')
        self.ax = self.fig.add_subplot(111)  # 111 表示 1行1列第1个（即整张图只有一个图表）
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background: transparent;")

    def update_chart(self, stats):
        """
        根据统计数据更新饼图显示。
        参数 stats: 列表，如 [{'category': '餐饮', 'total': 350.5}, ...]
        如果 stats 为空，显示"暂无数据"的提示文字。
        """
        self.ax.clear()
        if not stats:
            # 没有数据时，居中显示提示文字
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
            data, labels=None, autopct='%1.1f%%',    # autopct 在每个扇形上显示百分比
            colors=self.PALETTE[:len(labels)],        # 按顺序取配色
            startangle=90, pctdistance=0.58,           # 从顶部(90°)开始绘制
            wedgeprops={'linewidth': 2, 'edgecolor': 'white'}  # 扇形之间有白色分隔线
        )
        for t in autotexts:
            t.set_fontsize(9)
            t.set_fontweight('bold')
            t.set_color('#555')

        # 图例移到右侧（注：bbox_to_anchor 控制图例的位置，loc 是参考点）
        self.ax.legend(
            wedges, labels,
            loc='center left',
            bbox_to_anchor=(1, 0.5),
            fontsize=11,
            frameon=False,         # 图例不加外框
            labelspacing=0.8       # 图例项之间的行距
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
        font-size: 26px;
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
        font-size: 15px;
        font-weight: bold;
        color: {Colors.TEXT_SECONDARY};
        margin-bottom: 2px;
    """)
    return label


# ============================================
# 贪吃蛇游戏组件（QPainter 自绘制）
# ============================================
class SnakeGameWidget(QWidget):
    """贪吃蛇 — 用 QPainter 在画布上绘制蛇、食物、网格"""

    CELL = 25           # 每格像素大小
    COLS = 20           # 横向格子数
    ROWS = 20           # 纵向格子数
    START_SPEED = 120   # 初始速度（毫秒/步，越小越快）

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # 固定画布大小：棋盘 + 边框 + 底部分数区
        self.W = self.COLS * self.CELL + 2
        self.H = self.ROWS * self.CELL + 2
        self.setFixedSize(self.W, self.H + 36)
        self.reset_game()

    def reset_game(self):
        """初始化/重置游戏状态（等待点击开始）"""
        self.snake = [(self.ROWS // 2, self.COLS // 2 - 2),
                      (self.ROWS // 2, self.COLS // 2 - 3),
                      (self.ROWS // 2, self.COLS // 2 - 4)]
        self.direction = (0, 1)
        self.next_direction = (0, 1)
        self.food = self._place_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.waiting = True   # 等待点击"开始游戏"

        if hasattr(self, 'timer'):
            self.timer.stop()
            self.timer.deleteLater()  # 释放旧计时器，防止对象泄漏
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.setInterval(self.START_SPEED)
        # 不自动启动 timer，等点击"开始游戏"
        self.update()

    def start_game(self):
        """点击开始游戏按钮后启动（完全重置游戏状态）"""
        if not self.waiting:
            return
        # 完全重置游戏状态，避免 game_over/分数/蛇身残留
        self.reset_game()
        self.waiting = False
        self.timer.start()
        self.setFocus()  # 让游戏画布获得键盘焦点
        self.update()

    def _place_food(self):
        """在空白位置随机生成食物"""
        import random
        while True:
            pos = (random.randint(0, self.ROWS - 1),
                   random.randint(0, self.COLS - 1))
            if pos not in self.snake:
                return pos

    def _tick(self):
        """每帧更新：移动蛇、检测碰撞"""
        if self.game_over or self.paused:
            return

        # 防止 180 度掉头（一个 tick 内快速按两个方向键可能绕过 keyPressEvent 的检测）
        dr, dc = self.next_direction
        if (dr, dc) != (-self.direction[0], -self.direction[1]):
            self.direction = self.next_direction
        # 如果是反向，保持原方向，忽略这次掉头

        head_r, head_c = self.snake[0]
        dr, dc = self.direction
        new_head = (head_r + dr, head_c + dc)

        # 撞墙检测
        if not (0 <= new_head[0] < self.ROWS and 0 <= new_head[1] < self.COLS):
            self._die()
            return

        # 撞自己检测
        if new_head in self.snake:
            self._die()
            return

        self.snake.insert(0, new_head)

        # 吃到食物
        if new_head == self.food:
            self.score += 10
            # 棋盘占满 = 玩家胜利（防 while True 死循环）
            if len(self.snake) >= self.ROWS * self.COLS:
                self._die()
                self.update()
                return
            self.food = self._place_food()
            # 每 50 分加一次速
            if self.score % 50 == 0:
                new_interval = max(40, self.timer.interval() - 15)
                self.timer.setInterval(new_interval)
        else:
            self.snake.pop()  # 没吃到就去尾

        self.update()

    def _die(self):
        """游戏结束"""
        self.game_over = True
        self.waiting = True
        self.timer.stop()
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        """
        键盘按键处理。
        支持的按键：
        - 方向键 / WASD：控制蛇的移动方向
        - 空格 / P 键：暂停/继续游戏
        注：
        1. isAutoRepeat() 过滤掉按住不放产生的重复事件，防止方向键"加速"堆积。
        2. 禁止 180 度掉头（蛇不能直接掉头吃自己）。
        """
        # 忽略按键自动重复（按住不放时操作系统发送的重复事件）
        # 避免暂停键反复切换、方向键加速堆积
        if event.isAutoRepeat():
            return

        key = event.key()

        # 等待或游戏结束后，不响应方向键
        if self.waiting or self.game_over:
            return

        # 暂停
        if key in (Qt.Key.Key_Space, Qt.Key.Key_P):
            self.paused = not self.paused
            self.update()
            return

        # 方向键 + WASD（禁止原地掉头）
        if key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            if self.direction != (1, 0):
                self.next_direction = (-1, 0)
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            if self.direction != (-1, 0):
                self.next_direction = (1, 0)
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            if self.direction != (0, 1):
                self.next_direction = (0, -1)
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            if self.direction != (0, -1):
                self.next_direction = (0, 1)

    def paintEvent(self, event):
        """
        绘制整个游戏画面（每次蛇移动后自动调用 update() 触发重绘）。
        绘制顺序（从底到顶）：
        1. 棋盘背景（深蓝色 + 网格线）
        2. 食物（红色圆形）
        3. 蛇身（蛇头青色 + 蛇身渐变蓝绿，带圆角）
        4. 底部信息栏（得分 + 操作提示）
        5. 遮罩层（等待开始 / 游戏结束）

        注：QPainter 是 PyQt 的绘图工具，相当于一支画笔，
        可以画矩形、椭圆、文字等各种图形。
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 开启抗锯齿，让边缘更平滑

        w, h = self.W, self.H

        # ---- 棋盘背景 ----
        # 外层深灰边框 + 内层深蓝底色，形成立体感
        painter.fillRect(0, 0, w, h, QColor("#2c2c2c"))        # 外边框色
        painter.fillRect(1, 1, w - 2, h - 2, QColor("#16213e"))  # 棋盘底色

        # ---- 网格线（半透明的细线，营造"科技感"棋盘） ----
        painter.setPen(QPen(QColor("#1a1a3e"), 0.5))
        for i in range(self.COLS + 1):
            x = 1 + i * self.CELL
            painter.drawLine(x, 1, x, 1 + h - 2)
        for i in range(self.ROWS + 1):
            y = 1 + i * self.CELL
            painter.drawLine(1, y, 1 + w - 2, y)

        # ---- 食物（红色圆形，比格子略小，形成间距感） ----
        fr, fc = self.food
        fx = 1 + fc * self.CELL + 3
        fy = 1 + fr * self.CELL + 3
        fs = self.CELL - 6
        painter.setBrush(QBrush(QColor("#ff6b6b")))
        painter.setPen(Qt.PenStyle.NoPen)  # 不画轮廓线
        painter.drawEllipse(QRectF(fx, fy, fs, fs))

        # ---- 蛇身 ----
        # 蛇头是亮青色，身体从蓝渐变到深蓝（越靠近尾巴越暗）
        for i, (r, c) in enumerate(self.snake):
            sx = 1 + c * self.CELL + 2
            sy = 1 + r * self.CELL + 2
            ss = self.CELL - 4

            if i == 0:
                # 蛇头：亮青色，便于识别方向
                painter.setBrush(QBrush(QColor("#00d2ff")))
            else:
                # 蛇身：从蓝绿渐变到深蓝，越靠近尾巴颜色越暗
                t = i / max(len(self.snake), 1)
                g = int(180 - t * 100)   # 绿色分量递减
                b = int(220 - t * 80)    # 蓝色分量递减
                painter.setBrush(QBrush(QColor(0, g, b)))

            painter.setPen(Qt.PenStyle.NoPen)
            # 带圆角的小方块（圆角半径 5），让蛇看起来圆润可爱
            painter.drawRoundedRect(QRectF(sx, sy, ss, ss), 5, 5)

        # ---- 底部信息栏（画布下方） ----
        info_y = h + 6
        # 左侧：得分
        painter.setPen(QPen(QColor(Colors.TEXT_PRIMARY), 1))
        painter.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        painter.drawText(2, info_y + 18, f"🍎 得分: {self.score}")

        # 右侧：根据游戏状态显示不同提示文字
        hint = "←↑↓→ / WASD 移动    空格 暂停"
        if self.game_over:
            hint = "点击下方「开始游戏」重新开始"
        elif self.waiting:
            hint = "点击下方「开始游戏」按钮"
        elif self.paused:
            hint = "暂停中，按 空格 继续"
        painter.setPen(QPen(QColor(Colors.TEXT_MUTED), 1))
        painter.setFont(QFont("Microsoft YaHei", 11))
        tw = painter.fontMetrics().horizontalAdvance(hint)  # 计算文字宽度，用于右对齐
        painter.drawText(int(w - tw - 2), info_y + 18, hint)

        # ---- 等待开始遮罩（半透明黑色 + 白色提示文字） ----
        # 仅在等待且未死亡时显示，避免和游戏结束遮罩重叠
        if self.waiting and not self.game_over:
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 130))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
            painter.drawText(QRectF(0, h // 2 - 20, w, 40),
                             Qt.AlignmentFlag.AlignCenter, "准备开始！")

        # ---- 游戏结束遮罩（更暗 + 红色大字 + 最终得分） ----
        if self.game_over:
            painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 170))
            painter.setPen(QPen(QColor("#ff6b6b"), 1))
            painter.setFont(QFont("Microsoft YaHei", 26, QFont.Weight.Bold))
            painter.drawText(QRectF(0, h // 2 - 36, w, 36),
                             Qt.AlignmentFlag.AlignCenter, "游 戏 结 束")
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.setFont(QFont("Microsoft YaHei", 15))
            painter.drawText(QRectF(0, h // 2 + 8, w, 30),
                             Qt.AlignmentFlag.AlignCenter, f"最终得分: {self.score}")

        painter.end()


# ============================================
# 主窗口
# ============================================
class MainWindow(QMainWindow):
    """
    主窗口 — 应用的"外壳"，包含侧边栏和右侧页面区域。
    通俗理解：这就是打开应用后看到的大窗口，左边是导航栏，右边是内容页。
    所有页面的切换、数据的加载都通过这个窗口来调度。
    """

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("晚秋记账")
        self.setMinimumSize(1040, 680)  # 窗口最小尺寸，防止界面挤变形
        self.resize(1140, 780)          # 默认打开的窗口大小

        # 中央容器：整个窗口由左右两部分组成（侧边栏 + 内容区）
        # 注：QHBoxLayout 是水平布局，里面的控件从左到右排列
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)       # 左右不留空隙

        # ---- 侧边栏（左侧深色导航区） ----
        self._build_sidebar(main_layout)

        # ---- 右侧内容区（页面切换区） ----
        self._build_content(main_layout)

        # 启动时的初始化：加载分类列表、更新侧边栏支出数字
        self._load_categories_for_form()
        self._update_sidebar_summary()

    # ============================================
    # 侧边栏（深色高级感导航栏）
    # 通俗理解：这就是应用左侧那个深色竖条，包含：
    #   顶部标题 → 中间导航按钮 → 底部当月支出汇总
    # ============================================
    def _build_sidebar(self, parent_layout):
        """
        构建左侧导航侧边栏。
        结构从上到下：
        1. 标题区（橙色圆点 + "晚秋记账"）
        2. 分隔线
        3. 导航按钮组（记一笔、账单列表、月度统计、分类管理、贪吃蛇）
        4. 弹簧（把底部推到底部）
        5. 当月支出汇总
        """
        # 侧边栏容器：固定 240px 宽，深色背景
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"background: {Colors.SIDEBAR_BG};")

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        # ---- 标题区域：橙色装饰点 + "晚秋记账" ----
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(20, 24, 20, 18)

        # 橙色小圆点 — 视觉点缀，让标题区更有设计感
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {Colors.ACCENT}; font-size: 13px; background: transparent;")
        title_layout.addWidget(dot)

        title = QLabel("晚秋记账")
        title.setStyleSheet(f"""
            color: {Colors.SIDEBAR_TEXT};
            font-size: 20px;
            font-weight: bold;
            background: transparent;
            letter-spacing: 1.5px;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()

        side_layout.addWidget(title_container)

        # ---- 分隔线：半透明白色细线，区隔标题和导航 ----
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: rgba(255,255,255,0.06); max-height: 1px; margin: 0 16px;")
        side_layout.addWidget(sep)

        # ---- 导航按钮组 ----
        # 每个按钮是一个 QPushButton，设置了 checkable（可选中状态），
        # 选中的那个按钮会显示橙色左边框 + 文字加粗
        nav_items = [
            ('add-record', '✏️', '记一笔'),
            ('records-list', '📋', '账单列表'),
            ('statistics', '📊', '月度统计'),
            ('categories', '🏷️', '分类管理'),
            ('snake-game', '🐍', '贪吃蛇'),
        ]
        self.nav_btns = {}  # 用字典存储按钮引用，方便后面切换选中状态
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setSpacing(0)
        nav_layout.setContentsMargins(8, 12, 8, 12)

        for page_name, icon, label in nav_items:
            btn = QPushButton(f"  {icon}    {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName(f"nav_{page_name}")
            # 导航按钮的三种状态样式：
            # - 普通：透明背景、浅色文字
            # - 悬停：半透明白色蒙层
            # - 选中：橙色左边框 + 加粗白色文字
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.SIDEBAR_TEXT};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 6px;
                    padding: 13px 16px;
                    font-size: 16px;
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
            # 注：这里使用 lambda 闭包捕获 page_name 值，
            # p=page_name 确保每个按钮记住自己对应的页面名称
            btn.clicked.connect(lambda checked, p=page_name: self._switch_page(p))
            nav_layout.addWidget(btn)
            self.nav_btns[page_name] = btn

        side_layout.addWidget(nav_widget)

        # 弹簧：把下面所有内容推到底部
        # 通俗理解：像一个可伸缩的弹簧，自动填充中间的空余空间
        side_layout.addStretch()

        # ---- 底部分隔线 ----
        footer_sep = QFrame()
        footer_sep.setFrameShape(QFrame.Shape.HLine)
        footer_sep.setStyleSheet("background: rgba(255,255,255,0.06); max-height: 1px;")
        side_layout.addWidget(footer_sep)

        # ---- 底部当月支出汇总 ----
        footer = QWidget()
        footer.setStyleSheet("background: transparent;")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 16, 20, 22)
        footer_layout.setSpacing(6)

        # 标签："💰 当月支出"
        summary_icon = QLabel("💰 当月支出")
        summary_icon.setStyleSheet(f"""
            color: {Colors.SIDEBAR_TEXT_MUTED};
            font-size: 13px;
            background: transparent;
            letter-spacing: 0.3px;
        """)
        footer_layout.addWidget(summary_icon)

        # 金额：大号橙色数字，显示当月总支出
        self.summary_amount = QLabel("¥ 0.00")
        self.summary_amount.setStyleSheet(f"""
            color: {Colors.ACCENT};
            font-size: 26px;
            font-weight: bold;
            background: transparent;
        """)
        footer_layout.addWidget(self.summary_amount)

        side_layout.addWidget(footer)
        parent_layout.addWidget(sidebar)

        # 默认打开时选中第一个导航按钮（记一笔）
        self.nav_btns['add-record'].setChecked(True)

    # ============================================
    # 内容区（5个页面，通过 QStackedWidget 切换）
    # 注：QStackedWidget 就像一个"卡片堆"，同时只显示一张卡片，
    # 切换页面 = 翻到不同的卡片，其他页面保持在后台不动
    # ============================================
    def _build_content(self, parent_layout):
        """
        构建右侧内容区，内含 5 个页面：
        1. 记一笔（添加记录表单）
        2. 账单列表（表格 + 筛选）
        3. 月度统计（汇总卡片 + 饼图）
        4. 分类管理（网格布局 + 增删改）
        5. 贪吃蛇（小游戏）
        """
        content = QWidget()
        content.setStyleSheet(f"background: {Colors.PAGE_BG};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 32, 36, 32)  # 内容区四周留白

        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background: transparent;")
        # 按索引顺序添加页面，索引号对应 _switch_page 中的 page_map
        self.pages.addWidget(self._build_add_record_page())       # 索引 0
        self.pages.addWidget(self._build_records_list_page())     # 索引 1
        self.pages.addWidget(self._build_statistics_page())       # 索引 2
        self.pages.addWidget(self._build_categories_page())       # 索引 3
        self.pages.addWidget(self._build_snake_game_page())       # 索引 4
        content_layout.addWidget(self.pages)

        parent_layout.addWidget(content, 1)  # stretch=1 表示内容区占据剩余宽度

    def _switch_page(self, page_name):
        """
        切换内容区显示的页面。
        流程：
        1. 取消所有导航按钮的选中状态
        2. 高亮当前选中的按钮
        3. 翻页并加载对应数据

        参数 page_name 可选值：'add-record' | 'records-list' | 'statistics' | 'categories' | 'snake-game'
        """
        # 先全部取消选中
        for btn in self.nav_btns.values():
            btn.setChecked(False)
        # 再高亮当前按钮
        self.nav_btns[page_name].setChecked(True)

        # 页面名称到索引号的映射
        page_map = {'add-record': 0, 'records-list': 1, 'statistics': 2, 'categories': 3, 'snake-game': 4}

        # 离开贪吃蛇页面时，停止游戏计时器和轮询，防止后台空转消耗资源
        if self.pages.currentIndex() == page_map['snake-game'] and page_name != 'snake-game':
            self.snake_game.timer.stop()
            self.snake_game.waiting = True  # 让 _check_game_state 轮询自行退出

        # 切换到目标页面
        self.pages.setCurrentIndex(page_map[page_name])

        # 切换到对应页面时，刷新该页面的数据
        if page_name == 'records-list':
            self._load_records()
        elif page_name == 'statistics':
            self._load_statistics()
        elif page_name == 'categories':
            self._load_categories()
        elif page_name == 'add-record':
            self._load_categories_for_form()
        elif page_name == 'snake-game':
            self.snake_game.reset_game()

    # ============================================
    # 页面1：记一笔（表单卡片 + 渐变按钮 + 阴影效果）
    # 通俗理解：这就是"记一笔"页面，用表单方式填金额、分类、日期等，点击保存就记录下来
    # ============================================
    def _build_add_record_page(self):
        """
        构建"记一笔"页面。
        表单结构：
        - 金额输入框
        - 类型（支出/收入）+ 分类（两个下拉框并排）
        - 日期 + 备注（两个控件并排）
        - 保存按钮（橙色渐变）
        """
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        layout.addWidget(make_page_title("✏️  记一笔"))
        layout.addSpacing(4)

        # 表单卡片：白色圆角卡片内包含所有输入项
        card = make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(18)

        # 金额输入 — 占位符提示用户输入格式
        amt_layout = QVBoxLayout()
        amt_layout.setSpacing(6)
        amt_layout.addWidget(make_section_label("金额 (元)"))
        self.record_amount = QLineEdit()
        self.record_amount.setPlaceholderText("输入消费金额，例如：32.50")
        self.record_amount.setMinimumHeight(44)
        amt_layout.addWidget(self.record_amount)
        card_layout.addLayout(amt_layout)

        # 类型 + 分类 同行排列（用 QHBoxLayout 水平布局）
        row1 = QHBoxLayout()
        row1.setSpacing(24)

        # 类型下拉框：支出 / 收入
        type_layout = QVBoxLayout()
        type_layout.setSpacing(6)
        type_layout.addWidget(make_section_label("类型"))
        self.record_type = QComboBox()
        self.record_type.addItem('支出', 'expense')
        self.record_type.addItem('收入', 'income')
        self.record_type.setMinimumHeight(44)
        # 切换类型时，分类列表也需要更新（收入只显示"收入"分类）
        self.record_type.currentTextChanged.connect(self._load_categories_for_form)
        type_layout.addWidget(self.record_type)
        row1.addLayout(type_layout)

        # 分类下拉框：根据类型动态显示
        cat_layout = QVBoxLayout()
        cat_layout.setSpacing(6)
        cat_layout.addWidget(make_section_label("分类"))
        self.record_category = QComboBox()
        self.record_category.setMinimumHeight(44)
        cat_layout.addWidget(self.record_category)
        row1.addLayout(cat_layout)

        card_layout.addLayout(row1)

        # 日期 + 备注 同行排列
        row2 = QHBoxLayout()
        row2.setSpacing(24)

        # 日期选择器：默认今天，点击可弹出日历面板
        date_layout = QVBoxLayout()
        date_layout.setSpacing(6)
        date_layout.addWidget(make_section_label("日期"))
        self.record_date = QDateEdit()
        self.record_date.setCalendarPopup(True)
        self.record_date.setDate(QDate.currentDate())
        self.record_date.setMinimumHeight(44)
        date_layout.addWidget(self.record_date)
        row2.addLayout(date_layout)

        # 备注输入框：可选填
        note_layout = QVBoxLayout()
        note_layout.setSpacing(6)
        note_layout.addWidget(make_section_label("备注 (可选)"))
        self.record_note = QLineEdit()
        self.record_note.setPlaceholderText("例如：午餐外卖")
        self.record_note.setMinimumHeight(44)
        note_layout.addWidget(self.record_note)
        row2.addLayout(note_layout)

        card_layout.addLayout(row2)

        # 提交按钮 — 橙色渐变、大号字体，附带阴影让按钮"浮起来"
        card_layout.addSpacing(6)
        submit_btn = QPushButton("保存记录")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setMinimumHeight(48)
        submit_btn.setFixedWidth(160)
        # qlineargradient 创建从上到下的渐变：浅橙 → 深橙
        submit_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0a04b, stop:1 {Colors.ACCENT});
                color: #fff;
                border: none;
                border-radius: 12px;
                padding: 12px 32px;
                font-size: 17px;
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
        """
        加载分类到记一笔页面的下拉框。
        逻辑：
        - 如果当前选择"收入"，下拉框只显示"收入"分类
        - 如果当前选择"支出"，下拉框显示除"收入"外的所有分类
        这样用户不会在支出时选到"收入"，也不会在收入时选到"餐饮"。
        """
        cats = self.db.get_categories()
        rtype = self.record_type.currentData()
        filtered = [c for c in cats if c['name'] == '收入'] if rtype == 'income' else [c for c in cats if c['name'] != '收入']
        self.record_category.clear()
        self.record_category.addItem("请选择分类", None)  # 默认提示项，值为 None
        for c in filtered:
            self.record_category.addItem(f"{c['icon']}  {c['name']}", c['name'])

    def _submit_record(self):
        """
        校验表单并保存记一笔记录。
        校验规则：
        1. 金额必须是有效的数字（不是文字）
        2. 金额必须大于 0
        3. 必须选择一个分类
        保存成功后：清空表单、更新侧边栏当月支出数字、弹出成功提示。
        """
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

        # 保存成功后清空表单，方便继续记下一笔
        self.record_amount.clear()
        self.record_note.clear()
        self.record_category.setCurrentIndex(0)
        self.record_date.setDate(QDate.currentDate())
        self._update_sidebar_summary()
        QMessageBox.information(self, "成功", "✅ 记录保存成功！")

    # ============================================
    # 页面2：账单列表（可筛选月份、右键编辑/删除）
    # 通俗理解：这就是"账本"，按时间顺序列出所有记录，可以筛选月份、编辑、删除
    # ============================================
    def _build_records_list_page(self):
        """
        构建"账单列表"页面。
        结构：
        - 筛选栏（月份选择 + 清除按钮）
        - 数据表格（5列：日期、类型、分类、金额、备注）
        注：表格支持右键菜单（编辑/删除），行选中后可通过右键操作。
        """
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setSpacing(18)

        layout.addWidget(make_page_title("📋  账单列表"))

        # 筛选栏卡片：月份选择器 + 清除按钮
        filter_card = make_card()
        filter_card_layout = QHBoxLayout(filter_card)
        filter_card_layout.setContentsMargins(20, 10, 20, 10)
        filter_card_layout.setSpacing(12)

        month_label = QLabel("筛选月份")
        month_label.setStyleSheet(f"font-size: 15px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        filter_card_layout.addWidget(month_label)

        # 月份下拉框：自动生成最近 3 年的月份列表
        self.filter_month = QComboBox()
        self.filter_month.setMinimumWidth(130)
        self.filter_month.setMinimumHeight(38)
        now = QDate.currentDate()
        for y in range(now.year(), now.year() - 3, -1):
            for m in range(12, 0, -1):
                date = QDate(y, m, 1)
                if date <= now or (y == now.year() and m <= now.month()):
                    self.filter_month.addItem(date.toString('yyyy-MM'), date.toString('yyyy-MM'))
        self.filter_month.addItem("全部", None)  # 最后一项：显示所有记录
        self.filter_month.currentTextChanged.connect(self._load_records)
        filter_card_layout.addWidget(self.filter_month)

        # 清除筛选按钮：一键跳回"全部"
        clear_btn = QPushButton("清除筛选")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1.5px solid {Colors.CARD_BORDER};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
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

        # 数据表格：5 列均分拉伸，不可编辑，行选中模式
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels(['日期', '类型', '分类', '金额', '备注'])
        # Stretch 模式让所有列均分表格宽度，窗口变化时自动适应
        header = self.records_table.horizontalHeader()
        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        self.records_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # 选中整行
        self.records_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)         # 禁止直接编辑单元格
        self.records_table.setAlternatingRowColors(True)                                    # 隔行变色（斑马纹）
        self.records_table.setShowGrid(False)                                               # 隐藏表格网格线
        self.records_table.verticalHeader().setVisible(False)                               # 隐藏行号列
        self.records_table.setGraphicsEffect(shadow())

        # 右键菜单：连接信号到 _on_table_context_menu
        self.records_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.records_table.customContextMenuRequested.connect(self._on_table_context_menu)

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
                font-size: 15px;
            }}
            QTableWidget::item:alternate {{
                background: #fdf9f3;
            }}
            QHeaderView::section {{
                background: #fdf9f3;
                color: {Colors.TEXT_SECONDARY};
                font-size: 14px;
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
        """
        加载账单数据到表格中。
        从数据库读取记录（按筛选月份），逐行填充表格。
        每行的金额前带正负号（支出 - / 收入 +），颜色也区分（红/绿）。
        每条记录的 ID 存放在第一列的 UserRole 数据中，供右键编辑/删除时使用。
        """
        month = self.filter_month.currentData()
        records = self.db.get_records(month)

        self.records_table.setRowCount(len(records))
        for i, r in enumerate(records):
            # 日期列
            date_item = QTableWidgetItem(r['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.records_table.setItem(i, 0, date_item)

            # 类型列：支出显示红色，收入显示绿色
            type_text = '支出' if r['type'] == 'expense' else '收入'
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            type_item.setForeground(QColor(Colors.DANGER) if r['type'] == 'expense' else QColor(Colors.SUCCESS))
            self.records_table.setItem(i, 1, type_item)

            # 分类列
            cat_item = QTableWidgetItem(r['category'])
            cat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.records_table.setItem(i, 2, cat_item)

            # 金额列：加正负号和千分位分隔符
            sign = '-' if r['type'] == 'expense' else '+'
            amount_text = f"{sign}¥ {abs(r['amount']):,.2f}"
            amt_item = QTableWidgetItem(amount_text)
            amt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            amt_item.setForeground(QColor(Colors.DANGER) if r['type'] == 'expense' else QColor(Colors.SUCCESS))
            self.records_table.setItem(i, 3, amt_item)

            # 备注列：无备注时显示 "-"
            note_item = QTableWidgetItem(r['note'] or '-')
            note_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.records_table.setItem(i, 4, note_item)

            # 把记录 ID 存到第一列的隐藏数据中，右键菜单时需要用它定位是哪条记录
            date_item.setData(Qt.ItemDataRole.UserRole, r['id'])

    def _on_table_context_menu(self, pos):
        """
        表格右键菜单处理。
        在点击位置弹出菜单，提供"编辑"和"删除"两个选项。
        注：通过地图坐标转换（viewport().mapToGlobal）确定菜单弹出位置。
        """
        item = self.records_table.itemAt(pos)
        if item is None:
            return
        row = item.row()
        # 从第一列取记录 ID（之前在 _load_records 中存入的隐藏数据）
        date_item = self.records_table.item(row, 0)
        if date_item is None:
            return
        rec_id = date_item.data(Qt.ItemDataRole.UserRole)
        if rec_id is None:
            return

        menu = QMenu(self)
        edit_action = menu.addAction("✏  编辑")
        del_action = menu.addAction("🗑  删除")

        action = menu.exec(self.records_table.viewport().mapToGlobal(pos))
        if action == edit_action:
            self._edit_record(rec_id)
        elif action == del_action:
            self._delete_record(rec_id)

    def _edit_record(self, rec_id):
        """
        打开编辑弹窗修改一条记录。
        流程：根据 ID 找到记录 → 打开 EditDialog → 用户修改后点保存 → 更新数据库 → 刷新表格。
        """
        records = self.db.get_records()
        record = next((r for r in records if r['id'] == rec_id), None)
        if not record:
            return
        dlg = EditDialog(self.db, record, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:  # 用户点了"保存"
            data = dlg.result_data
            self.db.update_record(
                data['id'], data['amount'], data['type'],
                data['category'], data['subCategory'], data['note'], data['date']
            )
            self._load_records()
            self._update_sidebar_summary()

    def _delete_record(self, rec_id):
        """
        删除一条记录（弹出确认框防止误删）。
        注：删除操作不可撤销，所以必须弹确认框。
        """
        reply = QMessageBox.question(self, "确认删除", "确定要删除这条记录吗？此操作不可撤销。",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_record(rec_id)
            self._load_records()
            self._update_sidebar_summary()

    # ============================================
    # 页面3：月度统计（三张汇总卡片 + 饼图）
    # 通俗理解：查看某个月"花了多少、赚了多少、结余多少"，以及各分类的支出占比
    # ============================================
    def _build_statistics_page(self):
        """
        构建"月度统计"页面。
        结构：
        - 月份选择器
        - 三张汇总卡片（支出合计、收入合计、月度结余）
        - 饼图（各分类支出占比）
        """
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
        month_label.setStyleSheet(f"font-size: 15px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
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

        # 三张统计卡片（并排显示：支出、收入、结余）
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        # 支出卡片（红色数字）
        self.expense_card = self._make_stat_card("支出合计", "#e74c3c")
        self.expense_value = self._stat_card_value("#e74c3c")
        self.expense_card.layout().addWidget(self.expense_value)
        cards_row.addWidget(self.expense_card)

        # 收入卡片（绿色数字）
        self.income_card = self._make_stat_card("收入合计", "#27ae60")
        self.income_value = self._stat_card_value("#27ae60")
        self.income_card.layout().addWidget(self.income_value)
        cards_row.addWidget(self.income_card)

        # 结余卡片（橙色数字）—— 结余 = 收入 - 支出
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
        chart_title.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        chart_card_layout.addWidget(chart_title)
        self.pie_chart = PieChartCanvas()
        chart_card_layout.addWidget(self.pie_chart)
        layout.addWidget(chart_card, 1)  # stretch=1：饼图卡片自动填充剩余空间

        return page

    def _make_stat_card(self, title, accent_color):
        """
        创建一张统计卡片——白色圆角 + 彩色圆点 + 标题。
        参数：
        - title: 卡片标题，如"支出合计"
        - accent_color: 圆点和数字的颜色，如红色表示支出、绿色表示收入
        """
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
            f"font-size: 14px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        title_row.addWidget(title_label)
        title_row.addStretch()

        card_layout.addLayout(title_row)

        return card

    def _stat_card_value(self, color):
        """创建统计卡片中的大号金额数字标签"""
        lbl = QLabel("¥ 0.00")
        lbl.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 600;
            color: {color};
            background: transparent;
            padding-left: 2px;
        """)
        return lbl

    def _load_statistics(self):
        """
        加载月度统计数据并更新显示。
        从数据库获取当月统计数据，更新三张卡片和饼图。
        """
        month = self.stats_month.currentText()
        stats = self.db.get_monthly_stats(month)
        self.expense_value.setText(f"¥ {stats['expenseTotal']:,.2f}")
        self.income_value.setText(f"¥ {stats['incomeTotal']:,.2f}")
        # 结余 = 收入 - 支出
        balance = stats['incomeTotal'] - stats['expenseTotal']
        self.balance_value.setText(f"¥ {balance:,.2f}")
        self.pie_chart.update_chart(stats['expenseStats'])

    # ============================================
    # 页面4：分类管理（网格卡片 + 增删改）
    # 通俗理解：管理账本里的"类别"，可以新增自定义分类、编辑/删除自己的分类
    # ============================================
    def _build_categories_page(self):
        """
        构建"分类管理"页面。
        结构：
        - 添加入口（图标 + 名称 + 按钮）
        - 分类网格：4列排列，每个分类一张小卡片
          预设分类显示"默认"标签，自定义分类显示编辑/删除按钮
        """
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
        icon_label.setStyleSheet(f"font-size: 15px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
        add_card_layout.addWidget(icon_label)

        self.new_cat_icon = QLineEdit("📌")  # 默认图标
        self.new_cat_icon.setMaximumWidth(56)
        self.new_cat_icon.setMinimumHeight(44)
        self.new_cat_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        add_card_layout.addWidget(self.new_cat_icon)

        name_label = QLabel("名称")
        name_label.setStyleSheet(f"font-size: 15px; color: {Colors.TEXT_SECONDARY}; font-weight: bold; background: transparent;")
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
                font-size: 15px;
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

        # 分类网格容器 — 用 QGridLayout 实现 4 列排列
        # 每个分类是一张小卡片，预设分类标记"默认"，自定义分类可编辑/删除
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
        """
        加载分类数据到网格布局中。
        流程：
        1. 清空旧的网格卡片
        2. 从数据库读取所有分类
        3. 按 4 列排列，每个分类渲染为一张小卡片
        卡片内容：图标 + 名称 + [默认标签] 或 [编辑/删除按钮]
        """
        # 清除旧网格中的所有控件
        while self.categories_grid.count():
            item = self.categories_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cats = self.db.get_categories()
        cols = 4  # 每行 4 列
        for i, c in enumerate(cats):
            # 每张分类卡片的容器
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

            # 图标（大号 emoji）
            icon_label = QLabel(c['icon'])
            icon_label.setStyleSheet("font-size: 26px; background: transparent;")
            card_layout.addWidget(icon_label)

            # 分类名称
            name_label = QLabel(c['name'])
            name_label.setStyleSheet(f"font-size: 15px; font-weight: 500; color: {Colors.TEXT_PRIMARY}; background: transparent;")
            card_layout.addWidget(name_label)

            if c['is_default']:
                # 预设分类：显示"默认"标签，不可编辑和删除
                card_layout.addStretch()
                badge = QLabel("默认")
                badge.setStyleSheet(f"""
                    font-size: 12px;
                    color: {Colors.TEXT_MUTED};
                    background: #f5efe6;
                    padding: 3px 10px;
                    border-radius: 10px;
                """)
                card_layout.addWidget(badge)
            else:
                # 自定义分类：显示编辑和删除按钮
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
                        font-size: 16px;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        color: {Colors.ACCENT};
                        background: {Colors.ACCENT_LIGHT};
                    }}
                """)
                # 用 dict(c) 创建副本，防止 lambda 闭包引用问题
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
                        font-size: 17px;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        color: {Colors.DANGER};
                        background: #fde8e8;
                    }}
                """)
                del_btn.clicked.connect(lambda checked, cid=c['id'], cname=c['name']: self._delete_category(cid, cname))
                card_layout.addWidget(del_btn)

            # 计算网格位置：第 i 个卡片在第 row 行、第 col 列
            row, col = i // cols, i % cols
            self.categories_grid.addWidget(card, row, col)

    # ============================================
    # 页面5：贪吃蛇小游戏
    # 通俗理解：工作累了可以玩一局贪吃蛇放松。用方向键或 WASD 控制蛇的方向。
    # ============================================
    def _build_snake_game_page(self):
        """
        构建"贪吃蛇"游戏页面。
        结构：
        - 操作说明卡片
        - "开始游戏"按钮
        - 游戏画布（居中显示）
        注：按钮在游戏进行时会变灰并显示"游戏中..."，结束后恢复。
        """
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setSpacing(16)

        layout.addWidget(make_page_title("🐍  贪吃蛇"))
        layout.addSpacing(4)

        # 操作说明卡片（浅橙色背景 + 橙色边框，视觉上突出提示）
        hint_card = QWidget()
        hint_card.setStyleSheet(f"""
            background: {Colors.ACCENT_LIGHT};
            border: 1px solid {Colors.ACCENT};
            border-radius: 10px;
        """)
        hint_layout = QHBoxLayout(hint_card)
        hint_layout.setContentsMargins(16, 10, 16, 10)
        hint_label = QLabel("🎮  方向键/WASD 控制蛇的方向，空格暂停，吃到红色食物得分")
        hint_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; background: transparent; border: none;")
        hint_layout.addWidget(hint_label)
        layout.addWidget(hint_card)

        # 开始游戏按钮（居中）
        btn_wrapper = QWidget()
        btn_wrapper.setStyleSheet("background: transparent;")
        btn_layout = QHBoxLayout(btn_wrapper)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton("🎮  开 始 游 戏")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.ACCENT};
                color: #fff;
                border: none;
                border-radius: 12px;
                padding: 14px 48px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {Colors.ACCENT_HOVER};
            }}
        """)
        self.start_btn.clicked.connect(self._start_snake_game)
        btn_layout.addWidget(self.start_btn)
        layout.addWidget(btn_wrapper)

        # 游戏画布区（居中显示）
        game_wrapper = QWidget()
        game_wrapper.setStyleSheet("background: transparent;")
        game_layout = QHBoxLayout(game_wrapper)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.snake_game = SnakeGameWidget()
        self.snake_game.setStyleSheet("background: transparent;")
        game_layout.addWidget(self.snake_game)

        layout.addWidget(game_wrapper)
        layout.addStretch()

        return page

    def _start_snake_game(self):
        """
        点击"开始游戏"按钮的处理。
        按钮变灰显示"游戏中..."，启动游戏，并用定时器轮询游戏状态。
        游戏结束后按钮自动恢复为"开始游戏"。
        """
        self.snake_game.start_game()
        self.start_btn.setText("🎮  游戏中...")
        self.start_btn.setEnabled(False)
        # 启动轮询检测游戏是否结束（每 200ms 检查一次）
        self._check_game_state()

    def _check_game_state(self):
        """
        轮询检测贪吃蛇游戏状态。
        注：这里用 QTimer.singleShot 递归调用实现轮询，而不是在 SnakeGameWidget 中用信号通知。
        因为 SnakeGameWidget 不需要知道 MainWindow 的存在，职责分离更清晰。
        当 SnakeGameWidget.waiting 变为 True（游戏结束或重置），按钮恢复正常。
        """
        if self.snake_game.waiting:
            self.start_btn.setText("🎮  开 始 游 戏")
            self.start_btn.setEnabled(True)
        else:
            QTimer.singleShot(200, self._check_game_state)

    def _add_category(self):
        """
        新增自定义分类。
        校验：名称不能为空。
        如果分类名已存在，数据库会抛出 IntegrityError，弹出提示。
        """
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
        """
        删除自定义分类（预设分类不可删除，由数据库层双重保护）。
        删除前弹出确认框。
        """
        reply = QMessageBox.question(self, "确认删除", f"确定要删除分类「{cat_name}」吗？")
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_category(cat_id)
            self._load_categories()

    def _edit_category(self, category):
        """
        打开编辑弹窗修改分类名称和图标。
        如果名称修改后和已有分类冲突，数据库会报 IntegrityError。
        """
        dlg = CategoryEditDialog(category, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.result_data
            try:
                self.db.update_category(data['id'], data['name'], data['icon'])
                self._load_categories()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "错误", "修改失败，分类名称可能已存在")

    # ============================================
    # 侧边栏月度汇总更新
    # ============================================
    def _update_sidebar_summary(self):
        """
        更新侧边栏底部的当月支出汇总数字。
        注：每当添加/编辑/删除记录后，都需要调用这个方法刷新显示。
        """
        month = QDate.currentDate().toString('yyyy-MM')
        stats = self.db.get_monthly_stats(month)
        self.summary_amount.setText(f"¥ {stats['expenseTotal']:,.2f}")


# ============================================
# 程序启动入口
# 通俗解释：`if __name__ == '__main__'` 的意思是：
#   当直接运行 main.py 时（python main.py），下面的代码会执行；
#   当被其他文件 import 引用时（比如 test_main.py），下面的代码不会执行。
# 这样测试文件导入 Database 等类时不会弹出一个应用窗口。
# ============================================
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建 PyQt 应用程序实例
    app.setStyle('Fusion')        # 使用 Fusion 风格（跨平台一致的外观）

    # 设置全局默认字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 全局样式表 — 这是整个应用"变好看"的核心，
    # 相当于给所有控件统一穿上一套"衣服"
    app.setStyleSheet(GLOBAL_QSS)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())  # 进入事件循环，等待用户操作
