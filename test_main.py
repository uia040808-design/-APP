"""
晚秋记账 — 单元测试
测试范围：Database 类（核心数据操作）、工具函数
"""
import sys
import os
import tempfile
import shutil
import pytest

# 将 main.py 中的类导入到测试环境
# 注：PyQt6 可能没有安装，所以只测试不依赖 GUI 的部分
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入 main 模块（会触发 PyQt6 导入，所以用 mock 替代）
import importlib
import sqlite3


# ============================================
# 测试 Database 类
# 使用临时目录存放数据库，不影响用户真实数据
# ============================================

class TestDatabase:
    """测试所有数据库操作"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        每个测试前自动执行：
        1. 创建临时目录作为数据存储位置
        2. 模拟 APPDATA 环境变量指向临时目录
        3. 导入 Database 类
        4. 测试结束后清理临时目录
        """
        # 创建临时目录
        self.tmpdir = tempfile.mkdtemp(prefix='wq_test_')

        # 临时替换 APPDATA 环境变量
        self._old_appdata = os.environ.get('APPDATA', None)
        os.environ['APPDATA'] = self.tmpdir

        # 动态导入 Database（绕过 PyQt6 依赖）
        self._import_database()

        yield  # 这里是测试执行的分界点

        # 清理：恢复环境变量，删除临时目录
        if self._old_appdata:
            os.environ['APPDATA'] = self._old_appdata
        else:
            del os.environ['APPDATA']
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _import_database(self):
        """绕过 PyQt6 导入，只提取 Database 类"""
        import main
        self.Database = main.Database
        self.Colors = main.Colors

    # ========== 数据库初始化测试 ==========

    def test_init_creates_db_dir(self):
        """测试：初始化 Database 时会自动创建数据目录"""
        db = self.Database()
        db_dir = os.path.join(self.tmpdir, '晚秋记账')
        assert os.path.isdir(db_dir), "数据目录应该被创建"

    def test_init_creates_db_file(self):
        """测试：初始化后数据库文件存在"""
        db = self.Database()
        assert os.path.isfile(db.db_path), "数据库文件应该存在"

    def test_init_creates_tables(self):
        """测试：初始化后 categories 和 records 表存在"""
        db = self.Database()
        conn = db.get_conn()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t['name'] for t in tables]
        assert 'categories' in table_names, "categories 表应该存在"
        assert 'records' in table_names, "records 表应该存在"
        conn.close()

    def test_init_inserts_default_categories(self):
        """测试：首次初始化时自动插入 12 个预设分类"""
        db = self.Database()
        cats = db.get_categories()
        # 应该正好 12 个预设分类（全部 is_default=1）
        defaults = [c for c in cats if c['is_default'] == 1]
        assert len(defaults) == 12, f"应该有 12 个预设分类，实际有 {len(defaults)}"

    def test_init_only_runs_once(self):
        """测试：重复初始化不会重复插入分类"""
        db1 = self.Database()
        count1 = len(db1.get_categories())
        # 再创建一个 Database 实例
        db2 = self.Database()
        count2 = len(db2.get_categories())
        assert count1 == count2, "重复初始化不应增加分类数量"

    # ========== 分类 CRUD 测试 ==========

    def test_get_categories_returns_list(self):
        """测试：get_categories 返回列表"""
        db = self.Database()
        result = db.get_categories()
        assert isinstance(result, list), "应返回列表"

    def test_get_categories_has_required_fields(self):
        """测试：每个分类包含 id、name、icon、is_default 字段"""
        db = self.Database()
        cats = db.get_categories()
        for c in cats:
            assert 'id' in c, "缺少 id 字段"
            assert 'name' in c, "缺少 name 字段"
            assert 'icon' in c, "缺少 icon 字段"
            assert 'is_default' in c, "缺少 is_default 字段"

    def test_add_category_success(self):
        """测试：添加一个有效分类"""
        db = self.Database()
        before = len(db.get_categories())
        result = db.add_category('宠物', '🐱')
        after = len(db.get_categories())

        assert after == before + 1, "添加后分类数量应 +1"
        assert result['name'] == '宠物'
        assert result['icon'] == '🐱'
        assert 'id' in result

    def test_add_duplicate_category_raises_error(self):
        """测试：添加重名分类报错"""
        db = self.Database()
        db.add_category('宠物', '🐱')
        with pytest.raises(sqlite3.IntegrityError):
            db.add_category('宠物', '🐶')

    def test_delete_category(self):
        """测试：删除自定义分类"""
        db = self.Database()
        result = db.add_category('旅行', '✈️')
        before = len(db.get_categories())

        db.delete_category(result['id'])
        after = len(db.get_categories())

        assert after == before - 1, "删除后分类数量应 -1"

    def test_delete_default_category_fails_silently(self):
        """测试：删除预设分类不会被删除（is_default=1 保护）"""
        db = self.Database()
        cats = db.get_categories()
        default_ids = [c['id'] for c in cats if c['is_default'] == 1]
        before = len(cats)

        # 尝试删除第一个预设分类
        db.delete_category(default_ids[0])
        after = len(db.get_categories())

        assert after == before, "预设分类不应被删除"

    def test_update_category_success(self):
        """测试：更新自定义分类的名称和图标"""
        db = self.Database()
        result = db.add_category('运动', '⚽')
        cat_id = result['id']

        db.update_category(cat_id, '健身', '🏋️')

        cats = db.get_categories()
        updated = next(c for c in cats if c['id'] == cat_id)
        assert updated['name'] == '健身'
        assert updated['icon'] == '🏋️'

    def test_update_default_category_fails_silently(self):
        """测试：更新预设分类不会生效（is_default=1 保护）"""
        db = self.Database()
        cats = db.get_categories()
        default = [c for c in cats if c['is_default'] == 1][0]

        db.update_category(default['id'], '新名称', '🔧')

        cats_after = db.get_categories()
        still_default = next(c for c in cats_after if c['id'] == default['id'])
        assert still_default['name'] == default['name'], "预设分类名称不应被修改"

    # ========== 账单记录 CRUD 测试 ==========

    def test_add_record_success(self):
        """测试：添加一条支出记录"""
        db = self.Database()
        rec_id = db.add_record(
            amount=32.50, rtype='expense', category='餐饮',
            sub_category='外卖', note='午餐', date='2026-07-01'
        )
        assert rec_id is not None, "应返回记录 ID"
        assert rec_id > 0, "记录 ID 应大于 0"

    def test_add_income_record(self):
        """测试：添加一条收入记录"""
        db = self.Database()
        rec_id = db.add_record(
            amount=5000.00, rtype='income', category='收入',
            sub_category='', note='工资', date='2026-07-01'
        )
        records = db.get_records()
        added = next(r for r in records if r['id'] == rec_id)
        assert added['type'] == 'income'
        assert added['amount'] == 5000.00

    def test_add_record_with_empty_note(self):
        """测试：备注为空时也能正常添加"""
        db = self.Database()
        rec_id = db.add_record(
            amount=10, rtype='expense', category='交通',
            sub_category='', note='', date='2026-07-01'
        )
        records = db.get_records()
        added = next(r for r in records if r['id'] == rec_id)
        assert added['note'] == ''

    def test_get_records_returns_list(self):
        """测试：get_records 返回列表"""
        db = self.Database()
        result = db.get_records()
        assert isinstance(result, list)

    def test_get_records_empty_initially(self):
        """测试：新数据库没有记录"""
        db = self.Database()
        records = db.get_records()
        assert len(records) == 0, "新数据库应该没有记录"

    def test_get_records_after_add(self):
        """测试：添加记录后能查出来"""
        db = self.Database()
        db.add_record(15.00, 'expense', '餐饮', '', '早餐', '2026-07-01')
        db.add_record(8.00, 'expense', '交通', '', '公交', '2026-07-01')

        records = db.get_records()
        assert len(records) == 2

    def test_get_records_month_filter(self):
        """测试：按月份筛选记录"""
        db = self.Database()
        db.add_record(100, 'expense', '餐饮', '', '7月', '2026-07-01')
        db.add_record(200, 'expense', '餐饮', '', '8月', '2026-08-15')

        july = db.get_records(month='2026-07')
        aug = db.get_records(month='2026-08')

        assert len(july) == 1, "7月应该有 1 条记录"
        assert len(aug) == 1, "8月应该有 1 条记录"

    def test_get_records_order_desc(self):
        """测试：记录按日期倒序排列"""
        db = self.Database()
        db.add_record(100, 'expense', '餐饮', '', '早', '2026-07-01')
        db.add_record(200, 'expense', '交通', '', '晚', '2026-07-15')

        records = db.get_records()
        # 第一条应该是 7月15日（更新的日期）
        assert records[0]['date'] == '2026-07-15'

    def test_update_record(self):
        """测试：更新记录"""
        db = self.Database()
        rec_id = db.add_record(50, 'expense', '餐饮', '', '午餐', '2026-07-01')

        db.update_record(rec_id, 60, 'expense', '服饰', '', '衣服', '2026-07-02')

        records = db.get_records()
        updated = next(r for r in records if r['id'] == rec_id)
        assert updated['amount'] == 60
        assert updated['category'] == '服饰'
        assert updated['date'] == '2026-07-02'
        assert updated['note'] == '衣服'

    def test_delete_record(self):
        """测试：删除记录"""
        db = self.Database()
        rec_id = db.add_record(100, 'expense', '娱乐', '', '电影', '2026-07-01')

        before = len(db.get_records())
        db.delete_record(rec_id)
        after = len(db.get_records())

        assert after == before - 1

    # ========== 月度统计测试 ==========

    def test_get_monthly_stats_empty_month(self):
        """测试：没有记录的月份统计为 0"""
        db = self.Database()
        stats = db.get_monthly_stats('2026-07')

        assert stats['expenseTotal'] == 0
        assert stats['incomeTotal'] == 0
        assert stats['expenseStats'] == []

    def test_get_monthly_stats_expense_total(self):
        """测试：月度支出合计正确"""
        db = self.Database()
        db.add_record(100, 'expense', '餐饮', '', '', '2026-07-01')
        db.add_record(50, 'expense', '交通', '', '', '2026-07-02')
        db.add_record(30, 'expense', '娱乐', '', '', '2026-08-01')  # 不同月份

        stats = db.get_monthly_stats('2026-07')
        assert stats['expenseTotal'] == 150

    def test_get_monthly_stats_income_total(self):
        """测试：月度收入合计正确"""
        db = self.Database()
        db.add_record(5000, 'income', '收入', '', '工资', '2026-07-01')
        db.add_record(500, 'income', '收入', '', '兼职', '2026-07-15')

        stats = db.get_monthly_stats('2026-07')
        assert stats['incomeTotal'] == 5500

    def test_get_monthly_stats_category_breakdown(self):
        """测试：分类支出汇总正确"""
        db = self.Database()
        db.add_record(100, 'expense', '餐饮', '', '', '2026-07-01')
        db.add_record(50, 'expense', '餐饮', '', '', '2026-07-02')
        db.add_record(200, 'expense', '服饰', '', '', '2026-07-03')

        stats = db.get_monthly_stats('2026-07')

        # 按 total 降序排列
        assert len(stats['expenseStats']) == 2  # 只有两个分类
        assert stats['expenseStats'][0]['category'] == '服饰'  # 200 > 150
        assert stats['expenseStats'][0]['total'] == 200
        assert stats['expenseStats'][1]['category'] == '餐饮'
        assert stats['expenseStats'][1]['total'] == 150

    def test_get_monthly_stats_only_counts_selected_month(self):
        """测试：统计只计算选定月份的数据"""
        db = self.Database()
        db.add_record(111, 'expense', '餐饮', '', '', '2026-06-30')
        db.add_record(222, 'expense', '餐饮', '', '', '2026-07-01')
        db.add_record(333, 'expense', '餐饮', '', '', '2026-07-31')

        stats = db.get_monthly_stats('2026-07')
        assert stats['expenseTotal'] == 555  # 222 + 333

    # ========== 边界情况测试 ==========

    def test_record_with_large_amount(self):
        """测试：大额金额（99999999.99）"""
        db = self.Database()
        rec_id = db.add_record(
            99999999.99, 'income', '收入', '', '', '2026-07-01'
        )
        records = db.get_records()
        added = next(r for r in records if r['id'] == rec_id)
        assert added['amount'] == 99999999.99

    def test_category_name_with_special_chars(self):
        """测试：分类名包含特殊字符"""
        db = self.Database()
        result = db.add_category('A&B 测试-分类', '✅')
        assert result['name'] == 'A&B 测试-分类'


# ============================================
# 测试 Colors 类（颜色常量）
# ============================================

class TestColors:
    """测试设计系统颜色常量"""

    @pytest.fixture(autouse=True)
    def setup(self):
        import main
        self.Colors = main.Colors

    def test_colors_has_required_keys(self):
        """测试：Colors 包含所有必需的颜色常量"""
        required = [
            'SIDEBAR_BG', 'ACCENT', 'ACCENT_HOVER',
            'PAGE_BG', 'CARD_BG', 'TEXT_PRIMARY',
            'DANGER', 'SUCCESS'
        ]
        for key in required:
            assert hasattr(self.Colors, key), f"缺少颜色 {key}"

    def test_color_values_are_hex(self):
        """测试：颜色值是有效的 hex 格式"""
        import re
        for attr in dir(self.Colors):
            if attr.startswith('_'):
                continue
            value = getattr(self.Colors, attr)
            if isinstance(value, str) and value.startswith('#'):
                assert re.match(r'^#[0-9a-fA-F]{6}$', value), \
                    f"{attr} = {value} 不是有效的 hex 颜色"
