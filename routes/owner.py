from flask import Blueprint, request, jsonify
from models.owners import Owner
from models.house import House
from models import db
import logging
import re

owner_bp = Blueprint('owner', __name__)

@owner_bp.route('', methods=['GET'])
def get_owners():
    """获取业主列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    name = request.args.get('name', '')
    phone = request.args.get('phone', '')
    number = request.args.get('number', '')

    # 构建查询
    query = Owner.query
    if name:
        query = query.filter(Owner.name.like(f'%{name}%'))
    if phone:
        query = query.filter(Owner.phone.like(f'%{phone}%'))
    if number:
        query = query.filter(Owner.number.like(f'%{number}%'))

    # 获取分页数据
    pagination = query.paginate(page=page, per_page=size)
    owners = pagination.items
    total = pagination.total

    # 转换为JSON
    data = [{
        'id': owner.id,
        'number': owner.number,
        'name': owner.name,
        'gender': owner.gender,
        'age': owner.age,
        'phone': owner.phone,
        'id_card': owner.id_card,
        'houses': [house.to_dict() for house in owner.houses]
    } for owner in owners]

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': data,
        'total': total
    })

@owner_bp.route('', methods=['POST'])
def add_owner():
    """添加业主"""
    data = request.get_json()
    
    # 验证数据
    if not all(key in data for key in ['name', 'phone', 'idCard', 'number', 'gender']):
        return jsonify({
            'code': 400,
            'message': '缺少必要的字段'
        }), 400

    # 验证业主编号格式
    if not isinstance(data['number'], str) or len(data['number']) < 2 or len(data['number']) > 30:
        return jsonify({
            'code': 400,
            'message': '业主编号长度必须在2-30个字符之间'
        }), 400

    # 验证业主编号是否包含特殊字符
    if re.search(r'[^\w\u4e00-\u9fa5-]', data['number']):
        return jsonify({
            'code': 400,
            'message': '业主编号只能包含字母、数字、中文、下划线和横杠'
        }), 400

    # 检查手机号是否已存在
    if Owner.query.filter_by(phone=data['phone']).first():
        return jsonify({
            'code': 400,
            'message': '该手机号已被注册'
        }), 400

    # 检查业主编号是否已存在
    if Owner.query.filter_by(number=data['number']).first():
        return jsonify({
            'code': 400,
            'message': '该业主编号已存在'
        }), 400

    try:
        # 创建业主
        owner = Owner(
            number=data['number'],
            name=data['name'],
            gender=data['gender'],
            age=data.get('age'),
            phone=data['phone'],
            id_card=data['idCard']
        )
        db.session.add(owner)

        # 处理房屋关联
        if 'house_numbers' in data and data['house_numbers']:
            houses = House.query.filter(House.number.in_(data['house_numbers'])).all()
            owner.houses.extend(houses)

        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '添加成功',
            'data': {
                'id': owner.id,
                'number': owner.number,
                'name': owner.name,
                'gender': owner.gender,
                'age': owner.age,
                'phone': owner.phone,
                'id_card': owner.id_card,
                'houses': [house.to_dict() for house in owner.houses]
            }
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"添加业主失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加失败: {str(e)}'
        }), 500

@owner_bp.route('/<int:owner_id>', methods=['PUT'])
def update_owner(owner_id):
    """更新业主信息"""
    owner = Owner.query.get_or_404(owner_id)
    data = request.get_json()

    try:
        # 验证业主编号格式
        if 'number' in data:
            if not isinstance(data['number'], str) or len(data['number']) < 2 or len(data['number']) > 30:
                return jsonify({
                    'code': 400,
                    'message': '业主编号长度必须在2-30个字符之间'
                }), 400

            # 验证业主编号是否包含特殊字符
            if re.search(r'[^\w\u4e00-\u9fa5-]', data['number']):
                return jsonify({
                    'code': 400,
                    'message': '业主编号只能包含字母、数字、中文、下划线和横杠'
                }), 400

            # 检查业主编号是否已被其他业主使用
            if data['number'] != owner.number:
                existing_owner = Owner.query.filter_by(number=data['number']).first()
                if existing_owner and existing_owner.id != owner_id:
                    return jsonify({
                        'code': 400,
                        'message': '该业主编号已存在'
                    }), 400

        # 检查手机号是否已被其他业主使用
        if 'phone' in data and data['phone'] != owner.phone:
            if Owner.query.filter_by(phone=data['phone']).first():
                return jsonify({
                    'code': 400,
                    'message': '该手机号已被注册'
                }), 400

        # 更新基本信息
        if 'number' in data:
            owner.number = data['number']
        if 'name' in data:
            owner.name = data['name']
        if 'gender' in data:
            owner.gender = data['gender']
        if 'age' in data:
            owner.age = data['age']
        if 'phone' in data:
            owner.phone = data['phone']
        if 'idCard' in data:
            owner.id_card = data['idCard']

        # 更新房屋关联
        if 'house_numbers' in data:
            # 清除现有关联
            owner.houses = []
            # 添加新的关联
            if data['house_numbers']:
                houses = House.query.filter(House.number.in_(data['house_numbers'])).all()
                owner.houses.extend(houses)

        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'id': owner.id,
                'number': owner.number,
                'name': owner.name,
                'gender': owner.gender,
                'age': owner.age,
                'phone': owner.phone,
                'id_card': owner.id_card,
                'houses': [house.to_dict() for house in owner.houses]
            }
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"更新业主失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }), 500

@owner_bp.route('/<int:owner_id>', methods=['DELETE'])
def delete_owner(owner_id):
    """删除业主"""
    owner = Owner.query.get_or_404(owner_id)

    try:
        db.session.delete(owner)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

# 获取业主的房屋
@owner_bp.route('/<int:id>/houses', methods=['GET'])
def get_owner_houses(id):
    owner = Owner.query.get_or_404(id)
    houses = [house.to_dict() for house in owner.houses]
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': houses
    })

# 获取业主的缴费单
@owner_bp.route('/<int:id>/payment_bills', methods=['GET'])
def get_owner_payment_bills(id):
    owner = Owner.query.get_or_404(id)
    bills = [bill.to_dict() for bill in owner.payment_bills]
    return jsonify(bills)

# 获取业主的违规单
@owner_bp.route('/<int:id>/violation_bills', methods=['GET'])
def get_owner_violation_bills(id):
    owner = Owner.query.get_or_404(id)
    bills = [bill.to_dict() for bill in owner.violation_bills]
    return jsonify(bills)

# 获取业主的投诉单
@owner_bp.route('/<int:id>/complaint_bills', methods=['GET'])
def get_owner_complaint_bills(id):
    owner = Owner.query.get_or_404(id)
    bills = [bill.to_dict() for bill in owner.complaint_bills]
    return jsonify(bills)

# 获取业主的维修单
@owner_bp.route('/<int:id>/repair_bills', methods=['GET'])
def get_owner_repair_bills(id):
    owner = Owner.query.get_or_404(id)
    bills = [bill.to_dict() for bill in owner.repair_bills]
    return jsonify(bills)

@owner_bp.route('/search', methods=['GET'])
def search_owners():
    """搜索业主"""
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({
            'code': 200,
            'data': []
        })
    
    owners = Owner.query.filter(Owner.name.like(f'%{query}%')).all()
    
    return jsonify({
        'code': 200,
        'data': [owner.to_dict() for owner in owners]
    }) 