# 社区志愿者管理系统

Community Volunteer Management System

## 项目简介

社区志愿者管理系统是一个基于Web的志愿服务管理平台，旨在为社区志愿服务提供高效、便捷的管理和协调服务。系统采用现代化的技术栈，提供完整的志愿者管理、活动管理、签到管理等功能。

## 主要功能

### 用户管理
- 用户注册与登录
- 角色权限管理（管理员/志愿者）
- 个人信息管理

### 活动管理
- 活动发布与管理
- 活动分类与筛选
- 活动详情查看

### 志愿者服务
- 在线报名与取消
- 二维码智能签到
- 参与记录查询

### 数据统计
- 实时数据统计
- 活动参与分析
- 签到率统计

## 技术栈

### 后端技术
- **Python 3.8+**: 主要编程语言
- **Flask 3.1.2**: Web框架
- **SQLAlchemy 2.0.43**: ORM数据库操作
- **Flask-Login 0.6.3**: 用户认证
- **Flask-WTF 1.2.2**: 表单处理

### 前端技术
- **Bootstrap 5.1.3**: UI框架
- **Font Awesome 6.0.0**: 图标库
- **JavaScript**: 交互逻辑

### 数据库
- **SQLite**: 默认数据库（开发环境）
- **MySQL/PostgreSQL**: 生产环境推荐

## 快速开始

### 环境要求
- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd volunteer-management-system
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **初始化数据库**
```bash
python run.py
```

5. **访问系统**
打开浏览器访问: http://localhost:5002

### 默认账号
- **管理员**: admin / admin123
- **志愿者**: 注册新账号

## 项目结构

```
volunteer-management-system/
├── app.py                 # 主应用文件
├── models.py              # 数据模型
├── routes.py              # 路由定义
├── app_admin_api.py       # 管理员API
├── run.py                 # 启动文件
├── requirements.txt       # 依赖包
├── templates/             # 模板文件
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── login.html        # 登录页
│   ├── register.html     # 注册页
│   ├── activities.html   # 活动列表
│   ├── activity_detail.html # 活动详情
│   ├── qr_checkin.html   # 二维码签到
│   ├── about.html        # 关于页面
│   ├── statistics.html   # 统计页面
│   ├── admin/            # 管理员页面
│   └── errors/           # 错误页面
├── instance/             # 数据库文件
└── uploads/              # 上传文件
```

## 配置说明

### 环境变量
创建 `.env` 文件：
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///volunteer_system.db
```

### 数据库配置
- **SQLite** (默认): `sqlite:///volunteer_system.db`
- **MySQL**: `mysql://username:password@localhost/database`
- **PostgreSQL**: `postgresql://username:password@localhost/database`

## API 文档

### 基础URL
```
http://localhost:5002/api/v1
```

### 主要接口
- `GET /api/statistics` - 获取统计数据
- `GET /api/v1/admin/activities` - 获取活动列表
- `POST /api/v1/admin/activities` - 创建活动
- `PUT /api/v1/admin/activities/{id}` - 更新活动
- `POST /api/v1/admin/activities/{id}/publish` - 发布活动

详细API文档请参考 [附录B_API接口详细文档.md](附录B_API接口详细文档.md)

## 部署指南

### 开发环境
```bash
python run.py
```

### 生产环境
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

详细部署指南请参考 [附录A_系统安装部署指南.md](附录A_系统安装部署指南.md)

## 数据库设计

系统采用关系型数据库设计，主要包含以下表：
- `users` - 用户表
- `activities` - 活动表
- `activity_registrations` - 活动报名表
- `checkins` - 签到记录表
- `system_configs` - 系统配置表

详细数据库设计请参考 [附录C_数据库设计文档.md](附录C_数据库设计文档.md)

## 测试

### 运行测试
```bash
python -m pytest
```

### 功能测试
系统提供完整的功能测试脚本，包括：
- 用户注册登录测试
- 活动管理测试
- 签到功能测试
- API接口测试

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目链接: [https://github.com/your-username/volunteer-management-system](https://github.com/your-username/volunteer-management-system)
- 问题反馈: [Issues](https://github.com/your-username/volunteer-management-system/issues)
- 邮箱: contact@volunteer-system.com

## 更新日志

### v1.0.0 (2025-09-10)
- 初始版本发布
- 基础功能实现
- 用户管理、活动管理、签到管理
- 管理员后台
- 数据统计功能

---

**注意**: 这是一个学术项目，主要用于学习和研究目的。在生产环境中使用前，请确保进行充分的安全测试和性能优化。
