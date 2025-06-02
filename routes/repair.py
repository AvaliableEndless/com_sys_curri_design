from flask import Blueprint, request, jsonify
from models import db, RepairBill, RepairWorker, Owner, House
from datetime import datetime
import random
import logging

repair_bp = Blueprint('repair', __name__)

@repair_bp.route('', methods=['GET'])
def get_repair_bills():
    """获取维修单列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    owner_name = request.args.get('ownerName')
    house_number = request.args.get('houseNumber')
    
    query = RepairBill.query.join(Owner).join(House)
    
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
            if bill.worker:
                bill_dict['worker_name'] = bill.worker.name
            bills.append(bill_dict)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': bills,
            'total': pagination.total
        })
    except Exception as e:
        logging.error(f"获取维修单列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取维修单列表失败: {str(e)}'
        }), 500

@repair_bp.route('', methods=['POST'])
def add_repair_bill():
    """添加维修单"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['owner_id', 'house_id', 'content']
    if not all(field in data for field in required_fields):
        return jsonify({
            'code': 400,
            'message': '缺少必要的字段'
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
        
        bill = RepairBill(
            owner_id=owner.id,
            house_id=house.id,
            content=data['content'],
            repair_date=datetime.now(),
            status='未处理'
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
        logging.error(f"添加维修单失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加失败: {str(e)}'
        }), 500

@repair_bp.route('/<int:id>/complete', methods=['POST'])
def complete_repair(id):
    """完成维修"""
    bill = RepairBill.query.get_or_404(id)
    if bill.finish_date:
        return jsonify({
            'code': 400,
            'message': '该维修单已完成'
        }), 400
    
    data = request.get_json()
    if 'cost' not in data:
        return jsonify({
            'code': 400,
            'message': '缺少维修费用'
        }), 400
    
    try:
        bill.cost = data['cost']
        bill.finish_date = datetime.now()
        
        db.session.commit()
        
        # 添加业主、房屋和维修工信息
        bill_dict = bill.to_dict()
        if bill.owner:
            bill_dict['owner_name'] = bill.owner.name
        if bill.house:
            bill_dict['house_number'] = bill.house.number
        if bill.worker:
            bill_dict['worker_name'] = bill.worker.name
        
        return jsonify({
            'code': 200,
            'message': '完成成功',
            'data': bill_dict
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'完成失败: {str(e)}'
        }), 500 