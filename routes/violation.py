from flask import Blueprint, request, jsonify
from models.violation_bills import ViolationBill
from app import db
import logging

violation_bp = Blueprint('violation', __name__)

@violation_bp.route('', methods=['GET'])
def get_violation_bills():
    """获取违规单列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    owner_number = request.args.get('ownerNumber')
    house_number = request.args.get('houseNumber')
    
    query = ViolationBill.query
    
    if owner_number:
        query = query.filter(ViolationBill.owner_id.like(f'%{owner_number}%'))
    if house_number:
        query = query.filter(ViolationBill.house_id.like(f'%{house_number}%'))
    
    try:
        pagination = query.paginate(page=page, per_page=size)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': [bill.to_dict() for bill in pagination.items],
            'total': pagination.total
        })
    except Exception as e:
        logging.error(f"获取违规单列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取违规单列表失败: {str(e)}'
        }), 500

@violation_bp.route('', methods=['POST'])
def add_violation_bill():
    """添加违规单"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['owner_id', 'house_id', 'type', 
                      'fine_amount', 'status', 'worker', 'processed_at']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'code': 400,
                'message': f'缺少必要字段: {field}'
            }), 400
    
    try:
        bill = ViolationBill(
            owner_id=data['owner_id'],
            house_id=data['house_id'],
            type=data['type'],
            fine_amount=data['fine_amount'],
            status=data['status'],
            worker=data['worker'],
            processed_at=data['processed_at']
        )
        
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
            'message': f'添加失败: {str(e)}'
        }), 500

@violation_bp.route('/<int:id>', methods=['PUT'])
def update_violation_bill(id):
    """更新违规单"""
    bill = ViolationBill.query.get_or_404(id)
    data = request.get_json()
    
    bill.type = data.get('type', bill.type)
    bill.description = data.get('description', bill.description)
    bill.fine_amount = data.get('fine_amount', bill.fine_amount)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': bill.to_dict()
    })

@violation_bp.route('/<int:id>/process', methods=['POST'])
def process_violation(id):
    """处理违规"""
    bill = ViolationBill.query.get_or_404(id)
    data = request.get_json()
    
    if bill.status == '已处理':
        return jsonify({
            'code': 400,
            'message': '该违规单已处理'
        })
    
    bill.status = '已处理'
    bill.process_result = data.get('process_result', '')
    bill.processed_at = db.func.now()
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '处理成功',
        'data': bill.to_dict()
    })

@violation_bp.route('/<int:id>', methods=['DELETE'])
def delete_violation_bill(id):
    """删除违规单"""
    bill = ViolationBill.query.get_or_404(id)
    
    try:
        db.session.delete(bill)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}'
        }), 500 