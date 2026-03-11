"""
路由定义
Routes Definition
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone


def now_beijing():
    """获取当前北京时间（无时区信息，与数据库兼容）"""
    utc = datetime.now(timezone.utc)
    beijing = utc.astimezone(timezone(timedelta(hours=8)))
    # 返回无时区的时间对象，与数据库兼容
    return beijing.replace(tzinfo=None)
import qrcode
import io
import base64
import secrets
import json

from app import app, db
from models import User, Activity, ActivityRegistration, CheckIn, SystemConfig

# ==================== 基础页面路由 ====================

@app.route('/')
def index():
    """首页 - 显示活动列表"""
    activities = Activity.query.filter_by(status='published').order_by(Activity.start_time.desc()).limit(6).all()
    return render_template('index.html', activities=activities)

@app.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

# ==================== 用户认证路由 ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        real_name = request.form.get('real_name')
        phone = request.form.get('phone')
        
        # 验证输入
        if not all([username, email, password]):
            flash('请填写所有必填字段', 'error')
            return render_template('register.html')
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html')
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            real_name=real_name,
            phone=phone,
            role='volunteer'
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = now_beijing()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('已成功登出', 'info')
    return redirect(url_for('index'))

# ==================== 活动管理路由 ====================

@app.route('/activities')
def activities():
    """活动列表页面"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'published')
    
    query = Activity.query
    if status != 'all':
        query = query.filter_by(status=status)
    
    activities = query.order_by(Activity.start_time.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('activities.html', activities=activities, current_status=status)

@app.route('/activity/<int:activity_id>')
def activity_detail(activity_id):
    """活动详情页面"""
    activity = Activity.query.get_or_404(activity_id)
    
    # 检查用户是否已报名（且未取消）
    is_registered = False
    user_checkin = None
    if current_user.is_authenticated:
        registration = ActivityRegistration.query.filter_by(
            activity_id=activity_id, user_id=current_user.id
        ).first()
        is_registered = registration is not None and registration.status == 'registered'
        # 获取用户的签到记录
        if is_registered:
            user_checkin = CheckIn.query.filter_by(
                activity_id=activity_id, user_id=current_user.id
            ).first()
    
    # 获取参与者列表
    participants = ActivityRegistration.query.filter_by(
        activity_id=activity_id, status='registered'
    ).join(User).all()
    
    return render_template('activity_detail.html',
                         activity=activity,
                         is_registered=is_registered,
                         user_checkin=user_checkin,
                         participants=participants)

@app.route('/activity/register/<int:activity_id>', methods=['POST'])
@login_required
def register_activity(activity_id):
    """报名活动"""
    try:
        # 使用行锁查询活动，防止竞态条件
        activity = Activity.query.with_for_update().get_or_404(activity_id)

        # 检查是否已报名
        existing_registration = ActivityRegistration.query.filter_by(
            activity_id=activity_id, user_id=current_user.id
        ).first()

        if existing_registration:
            if existing_registration.status == 'registered':
                flash('您已经报名了该活动', 'warning')
                return redirect(url_for('activity_detail', activity_id=activity_id))
            elif existing_registration.status == 'cancelled':
                # 重新报名
                existing_registration.status = 'registered'
                existing_registration.registered_at = now_beijing()
                activity.current_participants += 1
                db.session.commit()
                flash('重新报名成功！', 'success')
                return redirect(url_for('activity_detail', activity_id=activity_id))

        # 检查活动是否可以报名（带锁的情况下再次检查）
        if not activity.can_register():
            flash('该活动无法报名', 'error')
            return redirect(url_for('activity_detail', activity_id=activity_id))

        # 创建报名记录
        registration = ActivityRegistration(
            activity_id=activity_id,
            user_id=current_user.id,
            status='registered'
        )

        db.session.add(registration)
        activity.current_participants += 1
        db.session.commit()
        flash('报名成功！', 'success')
    except Exception as e:
        db.session.rollback()
        flash('报名失败，请重试', 'error')

    return redirect(url_for('activity_detail', activity_id=activity_id))

@app.route('/activity/cancel/<int:activity_id>', methods=['POST'])
@login_required
def cancel_activity(activity_id):
    """取消报名"""
    activity = Activity.query.get_or_404(activity_id)
    
    registration = ActivityRegistration.query.filter_by(
        activity_id=activity_id, user_id=current_user.id
    ).first()
    
    if not registration:
        flash('您未报名该活动', 'error')
        return redirect(url_for('activity_detail', activity_id=activity_id))

    if registration.status == 'cancelled':
        flash('您已经取消过该活动报名', 'warning')
        return redirect(url_for('activity_detail', activity_id=activity_id))

    if not activity.is_upcoming():
        flash('活动已开始，无法取消报名', 'error')
        return redirect(url_for('activity_detail', activity_id=activity_id))

    try:
        registration.status = 'cancelled'
        if activity.current_participants > 0:
            activity.current_participants -= 1
        db.session.commit()
        flash('已取消报名', 'info')
    except Exception as e:
        db.session.rollback()
        flash('取消失败，请重试', 'error')
    
    return redirect(url_for('activity_detail', activity_id=activity_id))

# ==================== 签到管理路由 ====================

@app.route('/checkin/qr/<int:activity_id>')
@login_required
def qr_checkin(activity_id):
    """二维码签到页面"""
    activity = Activity.query.get_or_404(activity_id)

    # 检查用户是否已报名
    registration = ActivityRegistration.query.filter_by(
        activity_id=activity_id, user_id=current_user.id, status='registered'
    ).first()

    if not registration:
        flash('请先报名该活动', 'error')
        return redirect(url_for('activity_detail', activity_id=activity_id))

    # 检查是否已签到
    checkin = CheckIn.query.filter_by(
        activity_id=activity_id, user_id=current_user.id
    ).first()

    if checkin:
        flash('您已经签到过了', 'warning')
        return redirect(url_for('activity_detail', activity_id=activity_id))

    # 检查是否在签到时间窗口内
    # 配置1: 活动开始前10分钟开始签到
    # 配置2: 活动开始后10-30分钟可以签到
    can_checkin, checkin_message = activity.can_checkin_with_message(
        checkin_before_minutes=10,
        checkin_start_after_minutes=None,  # 设为10表示开始后10分钟
        checkin_window_minutes=None        # 设为20表示20分钟窗口
    )

    if not can_checkin:
        flash(f'当前不在签到时间窗口内: {checkin_message}', 'warning')
        return redirect(url_for('activity_detail', activity_id=activity_id))

    # 生成二维码令牌
    qr_token = secrets.token_urlsafe(32)
    session[f'qr_token_{activity_id}'] = qr_token
    
    # 生成二维码
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"{request.url_root}checkin/qr/{activity_id}/scan?token={qr_token}")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    qr_code_data = base64.b64encode(img_buffer.getvalue()).decode()
    
    return render_template('qr_checkin.html', 
                         activity=activity, 
                         qr_code_data=qr_code_data,
                         qr_token=qr_token)

@app.route('/checkin/qr/<int:activity_id>/scan', methods=['POST'])
@login_required
def scan_qr_checkin(activity_id):
    """扫描二维码签到"""
    activity = Activity.query.get_or_404(activity_id)
    qr_token = request.form.get('qr_token')
    
    # 验证二维码令牌
    if qr_token != session.get(f'qr_token_{activity_id}'):
        return jsonify({'success': False, 'message': '无效的二维码'})
    
    # 检查用户是否已报名
    registration = ActivityRegistration.query.filter_by(
        activity_id=activity_id, user_id=current_user.id, status='registered'
    ).first()
    
    if not registration:
        return jsonify({'success': False, 'message': '请先报名该活动'})
    
    # 检查是否已签到
    existing_checkin = CheckIn.query.filter_by(
        activity_id=activity_id, user_id=current_user.id
    ).first()
    
    if existing_checkin:
        return jsonify({'success': False, 'message': '您已经签到过了'})
    
    # 创建签到记录
    checkin = CheckIn(
        activity_id=activity_id,
        user_id=current_user.id,
        qr_token=qr_token,
        device_info=request.headers.get('User-Agent', '')
    )
    
    try:
        db.session.add(checkin)
        db.session.commit()
        
        # 清除二维码令牌
        session.pop(f'qr_token_{activity_id}', None)
        
        return jsonify({'success': True, 'message': '签到成功！'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '签到失败，请重试'})

# ==================== 管理员路由 ====================

@app.route('/admin')
@login_required
def admin_dashboard():
    """管理员仪表板"""
    if not current_user.is_admin():
        flash('权限不足', 'error')
        return redirect(url_for('index'))
    
    # 统计数据
    total_users = User.query.count()
    total_activities = Activity.query.count()
    total_registrations = ActivityRegistration.query.count()
    total_checkins = CheckIn.query.count()
    
    # 最近活动
    recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_activities': total_activities,
        'total_registrations': total_registrations,
        'total_checkins': total_checkins,
        'recent_activities': recent_activities
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/activities')
@login_required
def admin_activities():
    """管理员活动管理"""
    if not current_user.is_admin():
        flash('权限不足', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    activities = Activity.query.order_by(Activity.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/activities.html', activities=activities)

@app.route('/admin/activities/new', methods=['GET', 'POST'])
@login_required
def admin_new_activity():
    """创建新活动"""
    if not current_user.is_admin():
        flash('权限不足', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')
        max_participants = int(request.form.get('max_participants', 0))
        requirements = request.form.get('requirements')
        
        if not all([title, start_time, end_time]):
            flash('请填写所有必填字段', 'error')
            return render_template('admin/new_activity.html')
        
        try:
            activity = Activity(
                title=title,
                description=description,
                start_time=datetime.fromisoformat(start_time),
                end_time=datetime.fromisoformat(end_time),
                location=location,
                max_participants=max_participants,
                requirements=requirements,
                organizer_id=current_user.id,
                status='draft'
            )
            
            db.session.add(activity)
            db.session.commit()
            
            flash('活动创建成功', 'success')
            return redirect(url_for('admin_activities'))
        except Exception as e:
            db.session.rollback()
            flash('创建失败，请重试', 'error')
    
    return render_template('admin/new_activity.html')

# ==================== API 路由 ====================

@app.route('/api/statistics')
@login_required
def api_statistics():
    """获取统计数据API"""
    if not current_user.is_admin():
        return jsonify({'error': '权限不足'}), 403
    
    try:
        # 基础统计
        total_users = User.query.count()
        total_activities = Activity.query.count()
        total_registrations = ActivityRegistration.query.count()
        total_checkins = CheckIn.query.count()
        
        # 活动统计
        activity_stats = db.session.query(
            Activity.id,
            Activity.title,
            Activity.current_participants,
            db.func.count(CheckIn.id).label('checkin_count')
        ).outerjoin(CheckIn).group_by(Activity.id).all()
        
        stats = {
            'total_users': total_users,
            'total_activities': total_activities,
            'total_registrations': total_registrations,
            'total_checkins': total_checkins,
            'activity_stats': [
                {
                    'id': stat.id,
                    'title': stat.title,
                    'participants': stat.current_participants,
                    'checkins': stat.checkin_count
                }
                for stat in activity_stats
            ]
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 统计页面 ====================

@app.route('/statistics')
@login_required
def statistics():
    """统计页面"""
    if not current_user.is_admin():
        flash('权限不足', 'error')
        return redirect(url_for('index'))

    return render_template('statistics.html')

@app.route('/admin/member-checkin-stats')
@login_required
def member_checkin_stats():
    """成员签到率统计页面"""
    if not current_user.is_admin():
        flash('权限不足', 'error')
        return redirect(url_for('index'))

    # 获取所有志愿者用户
    volunteers = User.query.filter_by(role='volunteer').all()

    # 获取所有已发布的活动
    activities = Activity.query.filter_by(status='published').all()
    total_activities = len(activities)

    # 计算每个志愿者的签到率
    member_stats = []
    for user in volunteers:
        # 获取用户的报名记录
        registrations = ActivityRegistration.query.filter_by(
            user_id=user.id, status='registered'
        ).all()
        registered_count = len(registrations)

        # 获取用户的签到记录
        checkins = CheckIn.query.filter_by(user_id=user.id).all()
        checkin_count = len(checkins)

        # 计算签到率（报名且签到 / 报名总数）
        checkin_rate = round((checkin_count / registered_count * 100), 1) if registered_count > 0 else 0

        member_stats.append({
            'user': user,
            'registered_count': registered_count,
            'checkin_count': checkin_count,
            'checkin_rate': checkin_rate
        })

    # 按签到率排序（从高到低）
    member_stats.sort(key=lambda x: x['checkin_rate'], reverse=True)

    return render_template('admin/member_checkin_stats.html',
                         member_stats=member_stats,
                         total_activities=total_activities)