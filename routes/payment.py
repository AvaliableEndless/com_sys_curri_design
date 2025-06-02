from flask import Blueprint, request, jsonify
from models.payment_bills import PaymentBill
from models.owners import Owner
from models.house import House
from app import db
from datetime import datetime
import logging

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('', methods=['GET'])
def get_payment_bills():
    """获取缴费单列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    status = request.args.get('status')
    owner_number = request.args.get('ownerNumber')
    house_number = request.args.get('houseNumber')
    
    query = PaymentBill.query
    
    if status:
        query = query.filter(PaymentBill.status == status)
    if owner_number:
        query = query.filter(PaymentBill.owner_id.like(f'%{owner_number}%'))
    if house_number:
        query = query.filter(PaymentBill.house_id.like(f'%{house_number}%'))
    
    try:
        pagination = query.paginate(page=page, per_page=size)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': [bill.to_dict() for bill in pagination.items],
            'total': pagination.total
        })
    except Exception as e:
        logging.error(f"获取缴费单列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取缴费单列表失败: {str(e)}'
        }), 500

@payment_bp.route('', methods=['POST'])
def add_payment_bill():
    """添加缴费单"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['owner_id', 'house_id', 'type', 'amount']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'code': 400,
                'message': f'缺少必要字段：{field}'
            }), 400
    
    # 验证业主和房屋是否存在
    owner = Owner.query.filter_by(number=data['owner_id']).first()
    if not owner:
        return jsonify({
            'code': 400,
            'message': '业主不存在'
        }), 400
    
    house = House.query.filter_by(number=data['house_id']).first()
    if not house:
        return jsonify({
            'code': 400,
            'message': '房屋不存在'
        }), 400
    
    bill = PaymentBill(
        owner_id=data['owner_id'],
        house_id=data['house_id'],
        type=data['type'],
        amount=data['amount'],
        status=data.get('status', '未缴费'),
        description=data.get('description', '')
    )
    
    try:
        db.session.add(bill)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '添加成功',
            'data': bill.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@payment_bp.route('/<int:id>', methods=['PUT'])
def update_payment_bill(id):
    """更新缴费单"""
    bill = PaymentBill.query.get_or_404(id)
    data = request.get_json()
    
    bill.type = data.get('type', bill.type)
    bill.amount = data.get('amount', bill.amount)
    bill.description = data.get('description', bill.description)
    
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': bill.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500

@payment_bp.route('/<int:id>/pay', methods=['POST'])
def pay_bill(id):
    """处理缴费"""
    bill = PaymentBill.query.get_or_404(id)
    
    if bill.status == '已缴费':
        return jsonify({
            'code': 400,
            'message': '该账单已支付'
        })
    
    bill.status = '已缴费'
    bill.pay_time = datetime.now()
    
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '支付成功',
            'data': bill.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500 