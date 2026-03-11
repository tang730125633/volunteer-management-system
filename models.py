"""
数据模型定义
Data Models Definition
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from app import db


def now_beijing():
    """获取当前北京时间（无时区信息，与数据库兼容）"""
    utc = datetime.now(timezone.utc)
    beijing = utc.astimezone(timezone(timedelta(hours=8)))
    # 返回无时区的时间对象，与数据库兼容
    return beijing.replace(tzinfo=None)

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(255))
    role = db.Column(db.String(20), default='volunteer', index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=now_beijing, index=True)
    updated_at = db.Column(db.DateTime, default=now_beijing, onupdate=now_beijing)
    last_login = db.Column(db.DateTime)
    
    # 关系
    organized_activities = db.relationship('Activity', backref='organizer', lazy='dynamic')
    registrations = db.relationship('ActivityRegistration', backref='user', lazy='dynamic')
    checkins = db.relationship('CheckIn', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Activity(db.Model):
    """活动模型"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    max_participants = db.Column(db.Integer, default=0)
    current_participants = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='draft', index=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    requirements = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=now_beijing, index=True)
    updated_at = db.Column(db.DateTime, default=now_beijing, onupdate=now_beijing)
    published_at = db.Column(db.DateTime)

    # 关系
    registrations = db.relationship('ActivityRegistration', backref='activity', lazy='dynamic', cascade='all, delete-orphan')
    checkins = db.relationship('CheckIn', backref='activity', lazy='dynamic', cascade='all, delete-orphan')

    def is_published(self):
        """检查是否已发布"""
        return self.status == 'published'

    def is_ongoing(self):
        """检查是否进行中（使用北京时间）"""
        now = now_beijing()
        return self.start_time <= now <= self.end_time

    def is_upcoming(self):
        """检查是否即将开始（使用北京时间）"""
        return self.start_time > now_beijing()

    def is_ended(self):
        """检查是否已结束（使用北京时间）"""
        return self.end_time < now_beijing()
    
    def can_register(self):
        """检查是否可以报名"""
        # max_participants 为 0 表示不限制人数
        has_space = (self.max_participants == 0 or
                     self.current_participants < self.max_participants)
        return (self.is_published() and
                self.is_upcoming() and
                has_space)

    def can_checkin(self, checkin_before_minutes=10, checkin_start_after_minutes=None, checkin_window_minutes=None):
        """
        检查是否可以签到

        模式1: 活动开始前N分钟开始签到（默认10分钟），直到活动结束
            can_checkin(checkin_before_minutes=10)

        模式2: 活动开始后特定时间窗口签到
            can_checkin(checkin_start_after_minutes=10, checkin_window_minutes=20)
            表示活动开始10分钟后，20分钟内可以签到（即第10-30分钟）
        """
        now = now_beijing()

        if checkin_start_after_minutes is not None and checkin_window_minutes is not None:
            # 模式2: 活动开始后特定时间窗口
            checkin_start = self.start_time + timedelta(minutes=checkin_start_after_minutes)
            checkin_end = checkin_start + timedelta(minutes=checkin_window_minutes)
            return checkin_start <= now <= checkin_end
        else:
            # 模式1: 活动开始前N分钟开始签到，直到活动结束
            checkin_start = self.start_time - timedelta(minutes=checkin_before_minutes)
            return checkin_start <= now <= self.end_time

    def can_checkin_with_message(self, checkin_before_minutes=10, checkin_start_after_minutes=None, checkin_window_minutes=None):
        """
        检查是否可以签到，并返回状态信息
        返回: (can_checkin: bool, message: str)
        """
        now = now_beijing()

        if checkin_start_after_minutes is not None and checkin_window_minutes is not None:
            # 模式2: 活动开始后特定时间窗口
            checkin_start = self.start_time + timedelta(minutes=checkin_start_after_minutes)
            checkin_end = checkin_start + timedelta(minutes=checkin_window_minutes)

            if now < checkin_start:
                wait_minutes = int((checkin_start - now).total_seconds() / 60)
                return False, f"签到将在活动开始{checkin_start_after_minutes}分钟后开放，还需等待{wait_minutes}分钟"
            elif now > checkin_end:
                return False, f"签到已于活动开始后{checkin_start_after_minutes + checkin_window_minutes}分钟截止"
            else:
                return True, "签到开放中"
        else:
            # 模式1: 活动开始前N分钟开始签到，直到活动结束
            checkin_start = self.start_time - timedelta(minutes=checkin_before_minutes)

            if now < checkin_start:
                wait_minutes = int((checkin_start - now).total_seconds() / 60)
                return False, f"签到将在{checkin_before_minutes}分钟前开放，还需等待{wait_minutes}分钟"
            elif now > self.end_time:
                return False, "活动已结束，签到已截止"
            else:
                return True, "签到开放中"

    def get_checkin_status(self):
        """获取签到状态描述"""
        now = now_beijing()

        # 模式1: 开始前10分钟
        checkin_start_early = self.start_time - timedelta(minutes=10)
        if now < checkin_start_early:
            return '未到签到时间', '签到将在 ' + checkin_start_early.strftime('%H:%M') + ' 开放'
        elif checkin_start_early <= now < self.start_time:
            return '签到开放中', '活动即将开始，请尽快签到'
        elif self.start_time <= now <= self.end_time:
            return '签到开放中', '活动进行中'
        else:
            return '签到已结束', '活动已结束'

    def __repr__(self):
        return f'<Activity {self.title}>'

class ActivityRegistration(db.Model):
    """活动报名模型"""
    __tablename__ = 'activity_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=now_beijing, index=True)
    status = db.Column(db.String(20), default='registered', index=True)
    notes = db.Column(db.Text)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('activity_id', 'user_id', name='unique_registration'),)
    
    def __repr__(self):
        return f'<ActivityRegistration {self.user_id} -> {self.activity_id}>'

class CheckIn(db.Model):
    """签到模型"""
    __tablename__ = 'checkins'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkin_time = db.Column(db.DateTime, default=now_beijing, index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    qr_token = db.Column(db.String(100), index=True)
    device_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now_beijing)
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('activity_id', 'user_id', name='unique_checkin'),)
    
    def __repr__(self):
        return f'<CheckIn {self.user_id} -> {self.activity_id}>'

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text)
    description = db.Column(db.Text)
    config_type = db.Column(db.String(20), default='string')
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=now_beijing)
    updated_at = db.Column(db.DateTime, default=now_beijing, onupdate=now_beijing)
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'
