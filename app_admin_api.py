"""
管理员API接口
Admin API Endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone


def now_beijing():
    """获取当前北京时间（无时区信息，与数据库兼容）"""
    utc = datetime.now(timezone.utc)
    beijing = utc.astimezone(timezone(timedelta(hours=8)))
    # 返回无时区的时间对象，与数据库兼容
    return beijing.replace(tzinfo=None)
import os

from app import db
from models import User, Activity, ActivityRegistration, CheckIn

# 创建Blueprint
admin_api = Blueprint('admin_api', __name__)

@admin_api.before_request
@login_required
def require_admin():
    """要求管理员权限"""
    if not current_user.is_admin():
        return jsonify({'error': '权限不足'}), 403

# ==================== 活动管理API ====================

@admin_api.route('/admin/activities', methods=['GET'])
def get_activities():
    """获取活动列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', 'all')
        
        query = Activity.query
        if status != 'all':
            query = query.filter_by(status=status)
        
        activities = query.order_by(Activity.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'activities': [
                {
                    'id': activity.id,
                    'title': activity.title,
                    'description': activity.description,
                    'start_time': activity.start_time.isoformat(),
                    'end_time': activity.end_time.isoformat(),
                    'location': activity.location,
                    'max_participants': activity.max_participants,
                    'current_participants': activity.current_participants,
                    'status': activity.status,
                    'created_at': activity.created_at.isoformat()
                }
                for activity in activities.items
            ],
            'total': activities.total,
            'page': page,
            'per_page': per_page,
            'pages': activities.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api.route('/admin/activities', methods=['POST'])
def create_activity():
    """创建活动"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 创建活动
        activity = Activity(
            title=data['title'],
            description=data.get('description', ''),
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            location=data.get('location', ''),
            max_participants=data.get('max_participants', 0),
            requirements=data.get('requirements', ''),
            organizer_id=current_user.id,
            status='draft'
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'id': activity.id,
            'title': activity.title,
            'status': activity.status,
            'message': '活动创建成功'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/admin/activities/<int:activity_id>', methods=['PUT'])
def update_activity(activity_id):
    """更新活动"""
    try:
        activity = Activity.query.get_or_404(activity_id)
        data = request.get_json()
        
        # 更新字段
        if 'title' in data:
            activity.title = data['title']
        if 'description' in data:
            activity.description = data['description']
        if 'start_time' in data:
            activity.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            activity.end_time = datetime.fromisoformat(data['end_time'])
        if 'location' in data:
            activity.location = data['location']
        if 'max_participants' in data:
            activity.max_participants = data['max_participants']
        if 'requirements' in data:
            activity.requirements = data['requirements']
        
        activity.updated_at = now_beijing()
        db.session.commit()
        
        return jsonify({
            'id': activity.id,
            'title': activity.title,
            'message': '活动更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/admin/activities/<int:activity_id>/publish', methods=['POST'])
def publish_activity(activity_id):
    """发布活动"""
    try:
        activity = Activity.query.get_or_404(activity_id)
        
        if activity.status == 'published':
            return jsonify({'error': '活动已经发布'}), 400
        
        activity.status = 'published'
        activity.published_at = now_beijing()
        db.session.commit()
        
        return jsonify({
            'id': activity.id,
            'title': activity.title,
            'status': activity.status,
            'message': '活动发布成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/admin/activities/<int:activity_id>/delete', methods=['POST'])
def delete_activity(activity_id):
    """删除活动"""
    try:
        activity = Activity.query.get_or_404(activity_id)

        # 直接删除活动（级联删除报名和签到记录）
        db.session.delete(activity)
        db.session.commit()

        return jsonify({'message': '活动删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 用户管理API ====================

@admin_api.route('/admin/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role', 'all')
        
        query = User.query
        if role != 'all':
            query = query.filter_by(role=role)
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'real_name': user.real_name,
                    'phone': user.phone,
                    'role': user.role,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
                for user in users.items
            ],
            'total': users.total,
            'page': page,
            'per_page': per_page,
            'pages': users.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api.route('/admin/users/<int:user_id>/toggle', methods=['POST'])
def toggle_user_status(user_id):
    """切换用户状态"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 不能禁用自己
        if user.id == current_user.id:
            return jsonify({'error': '不能禁用自己'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'is_active': user.is_active,
            'message': f'用户{"激活" if user.is_active else "禁用"}成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 统计API ====================

@admin_api.route('/admin/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        # 基础统计
        total_users = User.query.count()
        total_activities = Activity.query.count()
        total_registrations = ActivityRegistration.query.count()
        total_checkins = CheckIn.query.count()
        
        # 活跃用户（最近30天有登录）
        thirty_days_ago = now_beijing() - timedelta(days=30)
        active_users = User.query.filter(User.last_login >= thirty_days_ago).count()
        
        # 活动状态统计
        draft_activities = Activity.query.filter_by(status='draft').count()
        published_activities = Activity.query.filter_by(status='published').count()
        completed_activities = Activity.query.filter_by(status='completed').count()
        
        # 月度统计
        current_month = now_beijing().replace(day=1)
        monthly_registrations = ActivityRegistration.query.filter(
            ActivityRegistration.registered_at >= current_month
        ).count()
        
        monthly_checkins = CheckIn.query.filter(
            CheckIn.checkin_time >= current_month
        ).count()
        
        return jsonify({
            'total_users': total_users,
            'total_activities': total_activities,
            'total_registrations': total_registrations,
            'total_checkins': total_checkins,
            'active_users': active_users,
            'activity_stats': {
                'draft': draft_activities,
                'published': published_activities,
                'completed': completed_activities
            },
            'monthly_stats': {
                'registrations': monthly_registrations,
                'checkins': monthly_checkins
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 签到管理API ====================

@admin_api.route('/admin/activities/<int:activity_id>/checkins', methods=['GET'])
def get_activity_checkins(activity_id):
    """获取活动签到记录"""
    try:
        activity = Activity.query.get_or_404(activity_id)

        checkins = CheckIn.query.filter_by(activity_id=activity_id).join(User).all()

        return jsonify({
            'activity_id': activity_id,
            'activity_title': activity.title,
            'checkins': [
                {
                    'id': checkin.id,
                    'user_id': checkin.user_id,
                    'username': checkin.user.username,
                    'real_name': checkin.user.real_name,
                    'checkin_time': checkin.checkin_time.isoformat(),
                    'latitude': checkin.latitude,
                    'longitude': checkin.longitude
                }
                for checkin in checkins
            ],
            'total': len(checkins)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_api.route('/admin/member-checkin-stats', methods=['GET'])
def get_member_checkin_stats():
    """获取成员签到率统计"""
    try:
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
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'email': user.email,
                'registered_count': registered_count,
                'checkin_count': checkin_count,
                'checkin_rate': checkin_rate
            })

        # 按签到率排序（从高到低）
        member_stats.sort(key=lambda x: x['checkin_rate'], reverse=True)

        return jsonify({
            'total_members': len(member_stats),
            'total_activities': total_activities,
            'members': member_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== 错误处理 ====================

@admin_api.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源未找到'}), 404

@admin_api.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': '内部服务器错误'}), 500