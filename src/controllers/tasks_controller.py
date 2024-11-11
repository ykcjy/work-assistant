import logging
import os
from datetime import datetime, timedelta
from ..models.tasks_model import TasksModel

class TasksController:
    def __init__(self, db):
        self.db = db
        self.model = TasksModel(db)
        self.logger = logging.getLogger(__name__)

    def is_holiday(self, date):
        """检查日期是否为节假日（包括周末）"""
        try:
            cursor = self.db.conn.cursor()
            
            # 首先检查是否在节假日表中
            cursor.execute('''
                SELECT is_workday 
                FROM holidays 
                WHERE date = ?
            ''', (date.strftime('%Y-%m-%d'),))
            
            result = cursor.fetchone()
            if result:
                return not result['is_workday']  # 如果是工作日返回False，否则返回True
            
            # 如果不在节假日表中，检查是否为周末
            return date.weekday() >= 5  # 5是周六，6是周日
            
        except Exception as e:
            self.logger.error(f"Error checking holiday: {e}")
            return False

    def get_last_workday_before(self, target_date):
        """获取指定日期前的最后一个工作日"""
        try:
            current_date = target_date - timedelta(days=1)  # 从前一天开始检查
            
            # 继续向前查找，直到找到工作日
            while self.is_holiday(current_date):
                current_date -= timedelta(days=1)
            
            return current_date
            
        except Exception as e:
            self.logger.error(f"Error getting last workday: {e}")
            return target_date - timedelta(days=1)  # 返回前一天作为默认值

    def get_tasks(self, include_completed=False):
        """获取任务列表"""
        try:
            return self.model.get_tasks(include_completed)
        except Exception as e:
            self.logger.error(f"Error getting tasks: {e}")
            raise

    def add_task(self, name, due_date, file_path=None, importance='普通'):
        """添加任务"""
        try:
            # 如果提供了文件路径，使用文件名作为任务名
            if file_path and not name:
                name = os.path.splitext(os.path.basename(file_path))[0]
            elif not name:
                raise ValueError("Task name cannot be empty")
                
            return self.model.add_task(name, due_date, file_path, importance)
        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            raise

    def update_task(self, task_id, name, due_date, importance):
        """更新任务信息"""
        try:
            # 验证重要程度是否为有效值
            valid_importance = ['普通', '重要', '紧急']
            if importance not in valid_importance:
                raise ValueError(f"Invalid importance value. Must be one of: {', '.join(valid_importance)}")
                
            # 调用模型更新任务
            return self.model.update_task(task_id, name, due_date, importance)
        except Exception as e:
            self.logger.error(f"Error updating task {task_id}: {e}")
            raise

    def complete_task(self, task_id):
        """完成任务"""
        try:
            return self.model.complete_task(task_id)
        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
            raise

    def cleanup_completed_tasks(self):
        """清理已完成任务"""
        try:
            return self.model.cleanup_completed_tasks()
        except Exception as e:
            self.logger.error(f"Error cleaning up tasks: {e}")
            raise

    def check_due_date(self, due_date_str, task=None):
        """检查任务到期情况，返回是否需要提醒和提醒消息"""
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            
            self.logger.info(f"\n=== 检查任务到期状态 ===")
            self.logger.info(f"到期日期: {due_date_str}")
            
            if task:
                task_dict = dict(task)
                self.logger.info(f"任务名称: {task_dict.get('name')}")
                self.logger.info(f"重要程度: {task_dict.get('importance')}")
                
                # 如果是紧急任务
                if task_dict.get('importance') == '紧急':
                    # 检查截止日期是否为节假日或节假日后的第一个工作日
                    is_holiday_period = False
                    
                    # 检查截止日期是否为节假日
                    if self.is_holiday(due_date):
                        is_holiday_period = True
                    else:
                        # 检查前一天是否为节假日（即是否为节假日后的第一个工作日）
                        prev_day = due_date - timedelta(days=1)
                        if self.is_holiday(prev_day):
                            is_holiday_period = True
                    
                    if is_holiday_period:
                        # 获取节假日前的最后两个工作日
                        last_workday = self.get_last_workday_before(due_date)
                        second_last_workday = self.get_last_workday_before(last_workday)
                        
                        self.logger.info(f"是否节假日期间: {is_holiday_period}")
                        self.logger.info(f"最后工作日: {last_workday}")
                        self.logger.info(f"倒数第二个工作日: {second_last_workday}")
                        self.logger.info(f"今天: {today}")
                        
                        if today <= second_last_workday:
                            return True, "需要今天完成"
                        elif today == last_workday:
                            return True, "需要今天完成"
                    
                    # 对于非节假日期间的紧急任务
                    days_left = (due_date - today).days
                    if days_left <= 2:
                        if days_left == 0:
                            return True, "今天到期"
                        elif days_left == 1:
                            return True, "明天到期"
                        else:
                            return True, "后天到期"
            
            # 如果已经过期
            if due_date < today:
                return True, "已过期"
                
            # 计算剩余天数
            days_left = (due_date - today).days
            
            # 如果是今天到期
            if days_left == 0:
                return True, "今天到期"
                
            # 如果是明天到期
            if days_left == 1:
                return True, "明天到期"
                
            # 如果是后天到期
            if days_left == 2:
                if not self.is_holiday(due_date):
                    return True, "后天到期"
            
            return False, ""
                
        except Exception as e:
            self.logger.error(f"Error checking due date: {e}")
            return False, ""

    def get_today_new_tasks_count(self):
        """获取今日新增的未完成任务数"""
        try:
            return self.model.get_today_new_tasks_count()
        except Exception as e:
            self.logger.error(f"Error getting today's new tasks count: {e}")
            raise

    def get_pending_tasks_count(self):
        """获取未完成任务总数"""
        try:
            return self.model.get_pending_tasks_count()
        except Exception as e:
            self.logger.error(f"Error getting pending tasks count: {e}")
            raise

    def restore_task(self, task_id):
        """恢复任务到未完成状态"""
        try:
            return self.model.restore_task(task_id)
        except Exception as e:
            self.logger.error(f"Error restoring task: {e}")
            raise

    def test_due_dates(self):
        """测试截止日期检查功能"""
        test_cases = [
            # 格式：(截止日期, 今天的日期, 预期结果)
            ('2024-10-01', '2024-09-29', True),   # 国庆节前两个工作日
            ('2024-10-01', '2024-09-28', False),  # 国庆节前三天（周六）
            ('2024-10-01', '2024-09-27', True),   # 国庆节前最后一个工作日
            ('2024-05-01', '2024-04-29', True),   # 劳动节前两个工作日
            ('2024-05-04', '2024-05-02', True),   # 劳动节后第一个工作日
            ('2024-01-01', '2023-12-29', True),   # 元旦前最后一个工作日
            ('2024-03-15', '2024-03-14', True),   # 普通工作日
            ('2024-03-16', '2024-03-14', False),  # 普通周末
        ]

        results = []
        for due_date, today, expected in test_cases:
            # 模拟当前日期
            current_date = datetime.strptime(today, '%Y-%m-%d').date()
            # 检查结果
            actual = self.is_due_soon(due_date)
            results.append({
                'due_date': due_date,
                'today': today,
                'expected': expected,
                'actual': actual,
                'passed': expected == actual
            })

        return results

    # 添加一个运行测试的方法
    def run_due_date_tests(self):
        """运行截止日期测试并显示结果"""
        results = self.test_due_dates()
        print("\n截止日期检查测试结果:")
        print("-" * 60)
        print(f"{'截止日期':<12} {'今天':<12} {'预期':<8} {'实际':<8} {'结果':<8}")
        print("-" * 60)
        for r in results:
            print(f"{r['due_date']:<12} {r['today']:<12} {str(r['expected']):<8} "
                  f"{str(r['actual']):<8} {'通过' if r['passed'] else '失败':<8}")
        print("-" * 60)

    def repair_tasks_data(self):
        """修复任务数据"""
        try:
            # 获取所有任务
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT id, name, file_path, due_date, status, completed_at 
                FROM pending_tasks
            ''')
            all_tasks = cursor.fetchall()
            
            # 修复每个任务的状态
            for task in all_tasks:
                # 如果任务有完成时间但状态不是completed，或者状态是completed但没有完成时间
                if (task['completed_at'] and task['status'] != 'completed') or \
                   (not task['completed_at'] and task['status'] == 'completed'):
                    # 重置为未完成状态
                    cursor.execute('''
                        UPDATE pending_tasks 
                        SET status = 'pending', completed_at = NULL 
                        WHERE id = ?
                    ''', (task['id'],))
            
            self.db.conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error repairing tasks data: {e}")
            return False

    def is_due_soon(self, due_date_str):
        """检查任务是否即将到期"""
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            today = datetime.now().date()
            
            # 如果已经过期
            if due_date <= today:
                return True
            
            # 计算剩余天数
            days_left = (due_date - today).days
            
            # 如果止日期是节假日，获取节假日前两个工作日
            if self.is_holiday(due_date):
                check_date = self.get_last_workday_before(due_date)
                if today <= check_date:
                    return True
            
            # 如果是未来两天内
            if 0 <= days_left <= 2:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking due soon: {e}")
            return False

    def get_task(self, task_id):
        """获取单个任务详情"""
        try:
            return self.model.get_task(task_id)
        except Exception as e:
            self.logger.error(f"Error getting task: {e}")
            raise

    def delete_task(self, task_id):
        """删除任务"""
        try:
            return self.model.delete_task(task_id)
        except Exception as e:
            self.logger.error(f"Error deleting task: {e}")
            raise

    def init_holidays(self, year):
        """初始化指定年份的节假日"""
        try:
            cursor = self.db.conn.cursor()
            
            # 清空指定年份的节假日数据
            cursor.execute('''
                DELETE FROM holidays 
                WHERE strftime('%Y', date) = ?
            ''', (str(year),))
            
            # 添加法定节假日
            holidays = [
                # 元旦
                (f"{year}-01-01", "元旦"),
                
                # 春节（预设）
                (f"{year}-02-10", "春节"),
                (f"{year}-02-11", "春节"),
                (f"{year}-02-12", "春节"),
                (f"{year}-02-13", "春节"),
                (f"{year}-02-14", "春节"),
                (f"{year}-02-15", "春节"),
                (f"{year}-02-16", "春节"),
                
                # 清明节（预设）
                (f"{year}-04-04", "清明节"),
                (f"{year}-04-05", "清明节"),
                
                # 劳动节
                (f"{year}-05-01", "劳动节"),
                (f"{year}-05-02", "劳动节"),
                (f"{year}-05-03", "劳动节"),
                (f"{year}-05-04", "劳动节"),
                (f"{year}-05-05", "动节"),
                
                # 端午节（预设）
                (f"{year}-06-22", "端午节"),
                (f"{year}-06-23", "端午"),
                (f"{year}-06-24", "端午节"),
                
                # 中秋节（预设）
                (f"{year}-09-29", "中秋节"),
                (f"{year}-09-30", "中秋节"),
                
                # 国庆节
                (f"{year}-10-01", "国庆节"),
                (f"{year}-10-02", "国庆节"),
                (f"{year}-10-03", "国庆节"),
                (f"{year}-10-04", "国庆节"),
                (f"{year}-10-05", "国庆节"),
                (f"{year}-10-06", "国庆节"),
                (f"{year}-10-07", "国庆节"),
            ]
            
            # 批量插入节假日
            cursor.executemany('''
                INSERT INTO holidays (date, name, is_workday)
                VALUES (?, ?, 0)
            ''', holidays)
            
            self.db.conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing holidays: {e}")
            return False

    def get_holidays(self, year, month):
        """获取指定月份的节假日数据"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT date, is_workday 
                FROM holidays 
                WHERE strftime('%Y', date) = ? 
                AND strftime('%m', date) = ?
            ''', (str(year), str(month).zfill(2)))
            
            holidays = {}
            for row in cursor.fetchall():
                date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                holidays[date] = bool(row['is_workday'])
                
            return holidays
            
        except Exception as e:
            self.logger.error(f"Error getting holidays: {e}")
            return {}

    def toggle_holiday(self, date, is_workday):
        """切换日期的节假日状态"""
        try:
            cursor = self.db.conn.cursor()
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM holidays WHERE date = ?', 
                         (date.strftime('%Y-%m-%d'),))
            
            if cursor.fetchone():
                # 更新现有记录
                cursor.execute('''
                    UPDATE holidays 
                    SET is_workday = ?, name = ?
                    WHERE date = ?
                ''', (1 if is_workday else 0, 
                     "调休" if is_workday else "节假日",
                     date.strftime('%Y-%m-%d')))
            else:
                # 添加新记录
                cursor.execute('''
                    INSERT INTO holidays (date, name, is_workday)
                    VALUES (?, ?, ?)
                ''', (date.strftime('%Y-%m-%d'),
                     "调休" if is_workday else "节假",
                     1 if is_workday else 0))
                
            self.db.conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error toggling holiday: {e}")
            raise

    def check_holiday_status(self, date):
        """检查指定日期的节假日状态"""
        try:
            cursor = self.db.conn.cursor()
            
            # 查询指定日期的节假日记录
            cursor.execute('''
                SELECT date, name, is_workday 
                FROM holidays 
                WHERE date = ?
            ''', (date.strftime('%Y-%m-%d'),))
            
            result = cursor.fetchone()
            if result:
                status = "工作日" if result['is_workday'] else "节假日"
                return f"{result['date']}: {status} ({result['name']})"
            else:
                # 如果不在节假日表中，检查是否为周末
                if date.weekday() >= 5:  # 5是周六，6是周日
                    return f"{date.strftime('%Y-%m-%d')}: 节假日 (周末)"
                else:
                    return f"{date.strftime('%Y-%m-%d')}: 工作日"
            
        except Exception as e:
            self.logger.error(f"Error checking holiday status: {e}")
            return f"Error checking status for {date.strftime('%Y-%m-%d')}"

    def check_dates_status(self, start_date, end_date):
        """���查一段时间内的节假日状态"""
        current_date = start_date
        results = []
        while current_date <= end_date:
            status = self.check_holiday_status(current_date)
            results.append(status)
            current_date += timedelta(days=1)
        return results