from flask import Blueprint, request, jsonify
from models import db, RepairWorker
from datetime import datetime
import logging

worker_bp = Blueprint('worker', __name__)

@worker_bp.route('/', methods=['GET'])
def get_repair_workers():
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)  # 修改为size
        name = request.args.get('name')
        worktype = request.args.get('worktype')  # 修改为worktype

        query = RepairWorker.query
        if name:
            query = query.filter(RepairWorker.name.like(f'%{name}%'))
        if worktype:
            query = query.filter(RepairWorker.worktype == worktype)

        pagination = query.order_by(RepairWorker.id.desc()).paginate(
            page=page, per_page=size
        )

        return jsonify({
            'code': 200,
            'data': [item.to_dict() for item in pagination.items],
            'total': pagination.total
        })
    except Exception as e:
        logging.error(f"获取维修工列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '获取维修工列表失败'
        }), 500

@worker_bp.route('/', methods=['POST'])
def create_repair_worker():
    try:
        data = request.get_json()
        worker = RepairWorker(
            number=data['number'],
            name=data['name'],
            worktype=data['worktype'],
            phone=data['phone'],
            address=data['address']
        )
        db.session.add(worker)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '添加成功',
            'data': worker.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"添加维修工失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加失败: {str(e)}'
        }), 500

@worker_bp.route('/<int:id>', methods=['PUT'])
def update_repair_worker(id):
    try:
        worker = RepairWorker.query.get_or_404(id)
        data = request.get_json()
        
        worker.number = data['number']
        worker.name = data['name']
        worker.worktype = data['worktype']
        worker.phone = data['phone']
        worker.address = data['address']
        
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': worker.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"更新维修工失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }), 500

@worker_bp.route('/<int:id>', methods=['DELETE'])
def delete_repair_worker(id):
    try:
        worker = RepairWorker.query.get_or_404(id)
        db.session.delete(worker)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"删除维修工失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}'
        }), 500

@worker_bp.route('/<int:id>/detail', methods=['GET'])
def get_repair_worker_detail(id):
    try:
        worker = RepairWorker.query.get_or_404(id)
        data = worker.to_dict()
        
        # 添加当前维修任务信息
        current_task = None
        for bill in worker.repair_bills:
            if bill.status == 'in_progress':
                current_task = {
                    'id': bill.id,
                    'content': bill.content,
                    'repair_date': bill.repair_date.isoformat(),
                    'owner_name': bill.owner.name if bill.owner else None,
                    'house_number': bill.house.number if bill.house else None
                }
                break
        data['current_task'] = current_task
        
        return jsonify({
            'code': 200,
            'data': data
        })
    except Exception as e:
        logging.error(f"获取维修工详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取详情失败: {str(e)}'
        }), 500

@worker_bp.errorhandler(Exception)
def handle_error(error):
    logging.error(f"维修工模块错误: {str(error)}")
    return jsonify({
        'code': 500,
        'message': str(error)
    }), 500