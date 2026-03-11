# 部署指南

## 1. GitHub 部署 ✅

已完成！仓库地址：https://github.com/tang730125633/volunteer-management-system

## 2. Vercel 部署

### 自动部署（推荐）

1. 访问 https://vercel.com/
2. 点击 "Add New Project"
3. 选择 `volunteer-management-system` 仓库
4. 点击 "Import"
5. 配置：
   - Framework Preset: `Other`
   - Build Command: 留空
   - Output Directory: 留空
6. 点击 "Deploy"

### 环境变量设置

在 Vercel Dashboard → Settings → Environment Variables 中添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SECRET_KEY` | 随机字符串 | Flask 密钥 |
| `DATABASE_URL` | 见下方 | Supabase 数据库连接 |

## 3. Supabase 数据库集成

### 步骤 1: 创建 Supabase 项目

1. 访问 https://supabase.com/
2. 点击 "New Project"
3. 填写信息：
   - Name: `volunteer-management`
   - Database Password: 保存好！
   - Region: Singapore / Tokyo
4. 等待创建完成

### 步骤 2: 获取连接信息

在 Supabase Dashboard：
1. 点击左侧 "Project Settings" → "Database"
2. 找到 "Connection string" 部分
3. 选择 "URI" 格式
4. 复制连接字符串（替换 [YOUR-PASSWORD]）

### 步骤 3: 初始化数据库

```bash
# 设置环境变量
export DATABASE_URL='postgresql://postgres:密码@db.xxxxx.supabase.co:5432/postgres'

# 运行初始化脚本
python supabase_setup.py
```

### 步骤 4: 配置 Vercel 环境变量

将 DATABASE_URL 添加到 Vercel 环境变量中。

## 4. 本地开发切换数据库

### 开发环境（SQLite）
```bash
# 不设置 DATABASE_URL，默认使用 SQLite
python run.py
```

### 生产环境（Supabase）
```bash
# 设置 Supabase 连接
export DATABASE_URL='postgresql://postgres:密码@db.xxxxx.supabase.co:5432/postgres'
python run.py
```

## 5. 验证部署

部署完成后访问：
- 网站: https://volunteer-management-system.vercel.app
- 管理员: admin / admin123

## 6. 故障排除

### 问题 1: 数据库连接失败
```
检查: DATABASE_URL 格式是否正确
检查: Supabase 项目是否已启动
检查: 密码是否正确（注意特殊字符需要 URL 编码）
```

### 问题 2: 数据库表不存在
```
解决: 运行 python supabase_setup.py 初始化
```

### 问题 3: 中文乱码
```
解决: Supabase 默认支持 UTF-8，无需额外配置
```

## 7. 安全配置清单

- [ ] 修改默认管理员密码
- [ ] 设置强 SECRET_KEY
- [ ] 启用 Supabase Row Level Security (RLS)
- [ ] 配置 CORS 域名限制
- [ ] 设置 HTTPS 强制跳转

## 8. 数据库备份

在 Supabase Dashboard 中：
1. 点击 "Database" → "Backups"
2. 可以手动创建备份或设置自动备份

## 技术支持

- Supabase 文档: https://supabase.com/docs
- Vercel 文档: https://vercel.com/docs
- Flask 文档: https://flask.palletsprojects.com/
