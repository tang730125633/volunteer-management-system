"""
系统启动文件
System Startup File
"""

import os
import sys
from app import app, db
from models import User, Activity, ActivityRegistration, CheckIn, SystemConfig

def create_admin_user():
    """创建管理员用户"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            real_name='系统管理员',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ 管理员用户创建成功 (用户名: admin, 密码: admin123)")

def create_sample_data():
    """创建示例数据"""
    # 检查是否已有数据
    if Activity.query.count() > 0:
        return
    
    from datetime import datetime
    
    # 创建示例活动
    activities = [
        {
            'title': '社区环境清洁活动',
            'description': '定期组织社区居民进行环境清洁，维护社区整洁',
            'start_time': '2025-09-15 09:00:00',
            'end_time': '2025-09-15 17:00:00',
            'location': '社区广场',
            'max_participants': 50,
            'requirements': '请自带清洁工具，穿着舒适的运动服'
        },
        {
            'title': '老年人关爱服务',
            'description': '为社区老年人提供生活帮助和心理关怀',
            'start_time': '2025-09-20 14:00:00',
            'end_time': '2025-09-20 18:00:00',
            'location': '社区活动中心',
            'max_participants': 30,
            'requirements': '有耐心，善于沟通'
        },
        {
            'title': '儿童安全教育讲座',
            'description': '为社区儿童举办安全知识讲座',
            'start_time': '2025-09-25 10:00:00',
            'end_time': '2025-09-25 12:00:00',
            'location': '社区会议室',
            'max_participants': 40,
            'requirements': '有教育经验者优先'
        }
    ]
    
    admin = User.query.filter_by(username='admin').first()
    
    for activity_data in activities:
        activity = Activity(
            title=activity_data['title'],
            description=activity_data['description'],
            start_time=datetime.fromisoformat(activity_data['start_time']),
            end_time=datetime.fromisoformat(activity_data['end_time']),
            location=activity_data['location'],
            max_participants=activity_data['max_participants'],
            requirements=activity_data['requirements'],
            organizer_id=admin.id,
            status='published'
        )
        db.session.add(activity)
    
    # 创建系统配置
    configs = [
        {
            'config_key': 'site_name',
            'config_value': '社区志愿者管理系统',
            'description': '网站名称',
            'config_type': 'string',
            'is_public': True
        },
        {
            'config_key': 'max_upload_size',
            'config_value': '16777216',
            'description': '最大上传文件大小（字节）',
            'config_type': 'number',
            'is_public': False
        }
    ]
    
    for config_data in configs:
        config = SystemConfig(**config_data)
        db.session.add(config)
    
    db.session.commit()
    print("✓ 示例数据创建成功")

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    # 创建所有表
    db.create_all()
    print("✓ 数据库表创建成功")
    
    # 创建管理员用户
    create_admin_user()
    
    # 创建示例数据
    create_sample_data()

def main():
    """主函数"""
    print("=" * 50)
    print("社区志愿者管理系统")
    print("Community Volunteer Management System")
    print("=" * 50)
    
    # 初始化数据库
    with app.app_context():
        init_database()
    
    print("正在启动系统...")
    print("访问地址: http://localhost:5002")
    print("管理员账号: admin / admin123")
    print("按 Ctrl+C 停止系统")
    print("=" * 50)
    
    # 启动应用
    try:
        app.run(debug=True, host='0.0.0.0', port=5002)
    except KeyboardInterrupt:
        print("\n系统已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()