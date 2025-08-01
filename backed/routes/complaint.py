from flask import Blueprint, request, jsonify
from models import db, ComplaintBill, Owner, House
from datetime import datetime
import logging

complaint_bp = Blueprint('complaint', __name__)

@complaint_bp.route('', methods=['GET'])
def get_complaint_bills():
    """获取投诉单列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    owner_name = request.args.get('ownerName')
    house_number = request.args.get('houseNumber')
    
    query = ComplaintBill.query.join(Owner).join(House)
    
    if owner_name:
        query = query.filter(Owner.name.like(f'%{owner_name}%'))
    if house_number:
        query = query.filter(House.number.like(f'%{house_number}%'))
    
    try:
        pagination = query.paginate(page=page, per_page=size)
        
        # 添加业主和房屋信息
        bills = []
        for bill in pagination.items:
            bill_dict = bill.to_dict()
            if bill.owner:
                bill_dict['owner_name'] = bill.owner.name
                bill_dict['owner_id'] = bill.owner.number  # 使用业主编号而不是ID
            if bill.house:
                bill_dict['house_number'] = bill.house.number
                bill_dict['house_id'] = bill.house.number  # 使用房屋编号而不是ID
            bills.append(bill_dict)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': bills,
            'total': pagination.total
        })
    except Exception as e:
        logging.error(f"获取投诉单列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取投诉单列表失败: {str(e)}'
        }), 500

@complaint_bp.route('', methods=['POST'])
def add_complaint_bill():
    """添加投诉单"""
    data = request.get_json()
    
    # 验证必要字段
    required_fields = ['owner_id', 'house_id', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'code': 400,
                'message': f'缺少必要字段: {field}'
            }), 400
    
    try:
        # 验证业主是否存在
        owner = Owner.query.filter_by(id=data['owner_id']).first()  # 使用业主ID查询
        if not owner:
            return jsonify({
                'code': 400,
                'message': '业主不存在'
            }), 400
        
        # 验证房屋是否存在
        house = House.query.filter_by(id=data['house_id']).first()  # 使用房屋ID查询
        if not house:
            return jsonify({
                'code': 400,
                'message': '房屋不存在'
            }), 400
        
        # 验证房屋是否属于该业主
        if house not in owner.houses:
            return jsonify({
                'code': 400,
                'message': '该房屋不属于所选业主'
            }), 400
        
        bill = ComplaintBill(
            owner_id=owner.id,
            house_id=house.id,
            content=data['content'],
            complaint_date=datetime.now(),
            process_result='未处理'
        )
        
        db.session.add(bill)
        db.session.commit()
        
        # 添加业主和房屋信息
        bill_dict = bill.to_dict()
        bill_dict['owner_name'] = owner.name
        bill_dict['owner_id'] = owner.number  # 返回业主编号
        bill_dict['house_number'] = house.number  # 返回房屋编号
        bill_dict['house_id'] = house.number  # 返回房屋编号
        
        return jsonify({
            'code': 200,
            'message': '添加成功',
            'data': bill_dict
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"添加投诉单失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加失败: {str(e)}'
        }), 500

@complaint_bp.route('/<int:id>', methods=['PUT'])
def update_complaint_bill(id):
    """更新投诉单"""
    bill = ComplaintBill.query.get_or_404(id)
    data = request.get_json()
    
    if bill.process_result != '未处理':
        return jsonify({
            'code': 400,
            'message': '只能修改未处理的投诉单'
        }), 400
    
    bill.content = data.get('content', bill.content)
    
    db.session.commit()
    
    # 添加业主和房屋信息
    bill_dict = bill.to_dict()
    if bill.owner:
        bill_dict['owner_name'] = bill.owner.name
    if bill.house:
        bill_dict['house_number'] = bill.house.number
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': bill_dict
    })

@complaint_bp.route('/<int:id>/process', methods=['POST'])
def process_complaint(id):
    """处理投诉"""
    bill = ComplaintBill.query.get_or_404(id)
    data = request.get_json()
    
    if bill.process_result != '未处理':
        return jsonify({
            'code': 400,
            'message': '该投诉单已处理'
        }), 400
    
    if 'process_result' not in data or 'operator' not in data:
        return jsonify({
            'code': 400,
            'message': '缺少处理结果或经办人信息'
        }), 400
    
    bill.process_result = data['process_result']
    bill.operator = data['operator']
    bill.processed_at = datetime.now()
    
    db.session.commit()
    
    # 添加业主和房屋信息
    bill_dict = bill.to_dict()
    if bill.owner:
        bill_dict['owner_name'] = bill.owner.name
    if bill.house:
        bill_dict['house_number'] = bill.house.number
    
    return jsonify({
        'code': 200,
        'message': '处理成功',
        'data': bill_dict
    })

@complaint_bp.route('/<int:id>', methods=['DELETE'])
def delete_complaint_bill(id):
    """删除投诉单"""
    bill = ComplaintBill.query.get_or_404(id)
    
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

@complaint_bp.route('/complaint_bills/<int:id>/detail', methods=['GET'])
def get_complaint_bill_detail(id):
    bill = ComplaintBill.query.get_or_404(id)
    data = bill.to_dict()
    
    # 添加业主和房屋信息
    if bill.owner:
        data['owner_name'] = bill.owner.name
    if bill.house:
        data['house_number'] = bill.house.number
    
    return jsonify(data) 