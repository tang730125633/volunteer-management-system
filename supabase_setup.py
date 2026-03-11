"""
Supabase 数据库初始化脚本
Supabase Database Setup Script
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def setup_supabase_database():
    """初始化 Supabase PostgreSQL 数据库"""

    # 从环境变量获取数据库 URL
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        print("❌ 错误: 未设置 DATABASE_URL 环境变量")
        print("请设置: export DATABASE_URL='postgresql://...'")
        return False

    # 处理 Supabase 连接字符串格式
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    print(f"🔄 正在连接数据库...")

    try:
        engine = create_engine(database_url)

        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ 数据库连接成功!")
            print(f"   PostgreSQL 版本: {version.split()[1]}")

        print("\n🔄 正在创建数据表...")

        # 创建表（与 models.py 对应）
        create_tables_sql = """
        -- 用户表
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            real_name VARCHAR(50),
            phone VARCHAR(20),
            avatar_url VARCHAR(255),
            role VARCHAR(20) DEFAULT 'volunteer',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        -- 活动表
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            location VARCHAR(200),
            max_participants INTEGER DEFAULT 0,
            current_participants INTEGER DEFAULT 0,
            status VARCHAR(20) DEFAULT 'draft',
            organizer_id INTEGER NOT NULL REFERENCES users(id),
            requirements TEXT,
            image_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP
        );

        -- 活动报名表
        CREATE TABLE IF NOT EXISTS activity_registrations (
            id SERIAL PRIMARY KEY,
            activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'registered',
            notes TEXT,
            UNIQUE(activity_id, user_id)
        );

        -- 签到表
        CREATE TABLE IF NOT EXISTS checkins (
            id SERIAL PRIMARY KEY,
            activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            checkin_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            latitude FLOAT,
            longitude FLOAT,
            qr_token VARCHAR(100),
            device_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(activity_id, user_id)
        );

        -- 系统配置表
        CREATE TABLE IF NOT EXISTS system_configs (
            id SERIAL PRIMARY KEY,
            config_key VARCHAR(100) UNIQUE NOT NULL,
            config_value TEXT,
            description TEXT,
            config_type VARCHAR(20) DEFAULT 'string',
            is_public BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 创建索引优化查询性能
        CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);
        CREATE INDEX IF NOT EXISTS idx_activities_start_time ON activities(start_time);
        CREATE INDEX IF NOT EXISTS idx_registrations_user ON activity_registrations(user_id);
        CREATE INDEX IF NOT EXISTS idx_registrations_activity ON activity_registrations(activity_id);
        CREATE INDEX IF NOT EXISTS idx_checkins_user ON checkins(user_id);
        CREATE INDEX IF NOT EXISTS idx_checkins_activity ON checkins(activity_id);
        """

        with engine.connect() as conn:
            conn.execute(text(create_tables_sql))
            conn.commit()

        print("✅ 数据表创建成功!")
        print("   - users (用户表)")
        print("   - activities (活动表)")
        print("   - activity_registrations (报名表)")
        print("   - checkins (签到表)")
        print("   - system_configs (系统配置表)")

        # 创建默认管理员账号
        print("\n🔄 创建默认管理员账号...")

        from werkzeug.security import generate_password_hash

        admin_password = generate_password_hash('admin123')

        with engine.connect() as conn:
            # 检查是否已有管理员
            result = conn.execute(text("SELECT id FROM users WHERE role = 'admin' LIMIT 1"))
            if not result.fetchone():
                conn.execute(text("""
                    INSERT INTO users (username, email, password_hash, real_name, role, is_active)
                    VALUES ('admin', 'admin@example.com', :password, '系统管理员', 'admin', TRUE)
                """), {"password": admin_password})
                conn.commit()
                print("✅ 默认管理员账号创建成功!")
                print("   用户名: admin")
                print("   密码: admin123")
            else:
                print("ℹ️  管理员账号已存在，跳过创建")

        print("\n🎉 Supabase 数据库初始化完成!")
        return True

    except OperationalError as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n请检查:")
        print("1. DATABASE_URL 是否正确")
        print("2. 网络是否可连接到 Supabase")
        print("3. Supabase 项目是否已启动")
        return False
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Supabase 数据库初始化工具")
    print("=" * 50)
    print()

    success = setup_supabase_database()

    if success:
        print("\n下一步:")
        print("1. 在 Vercel 中设置 DATABASE_URL 环境变量")
        print("2. 部署项目到 Vercel")
    else:
        print("\n请修复错误后重试")
