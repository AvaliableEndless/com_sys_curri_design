from flask import Blueprint, request, jsonify
from models.house import House
from app import db
import logging

house_bp = Blueprint('house', __name__)

@house_bp.route('', methods=['GET'])
def get_houses():
    """获取房屋列表"""
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    house_type = request.args.get('house_type')
    number = request.args.get('number')
    
    query = House.query
    
    if house_type:
        query = query.filter(House.house_type == house_type)
    if number:
        query = query.filter(House.number.like(f'%{number}%'))
    
    try:
        pagination = query.paginate(page=page, per_page=size)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': [house.to_dict() for house in pagination.items],
            'total': pagination.total
        })
    except Exception as e:
        logging.error(f"获取房屋列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取房屋列表失败: {str(e)}'
        }), 500

@house_bp.route('', methods=['POST'])
def add_house():
    """添加房屋"""
    data = request.get_json()
    
    # 检查房屋编号是否已存在
    if House.query.filter_by(number=data['number']).first():
        return jsonify({
            'code': 400,
            'message': '该房屋编号已存在'
        }), 400
    
    house = House(
        number=data['number'],
        area=data['area'],
        using_area=data['using_area'],
        house_type=data['house_type']
    )
    
    db.session.add(house)
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': house.to_dict()
    })

@house_bp.route('/<int:id>', methods=['PUT'])
def update_house(id):
    """更新房屋信息"""
    house = House.query.get_or_404(id)
    data = request.get_json()
    
    # 如果更新房屋编号，需要检查是否与其他房屋重复
    if 'number' in data and data['number'] != house.number:
        if House.query.filter_by(number=data['number']).first():
            return jsonify({
                'code': 400,
                'message': '该房屋编号已存在'
            }), 400
        house.number = data['number']
    
    house.area = data.get('area', house.area)
    house.using_area = data.get('using_area', house.using_area)
    house.house_type = data.get('house_type', house.house_type)
    
    db.session.commit()
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': house.to_dict()
    })

@house_bp.route('/<int:id>', methods=['DELETE'])
def delete_house(id):
    """删除房屋"""
    house = House.query.get_or_404(id)
    
    # 检查是否有关联数据
    if house.payment_bills.count() > 0:
        return jsonify({
            'code': 400,
            'message': '该房屋存在缴费记录，无法删除'
        }), 400
    
    if house.violation_bills.count() > 0:
        return jsonify({
            'code': 400,
            'message': '该房屋存在违规记录，无法删除'
        }), 400
    
    if house.complaint_bills.count() > 0:
        return jsonify({
            'code': 400,
            'message': '该房屋存在投诉记录，无法删除'
        }), 400
    
    if house.repair_bills.count() > 0:
        return jsonify({
            'code': 400,
            'message': '该房屋存在维修记录，无法删除'
        }), 400
    
    try:
        db.session.delete(house)
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

@house_bp.route('/search', methods=['GET'])
def search_houses():
    """搜索房屋"""
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({
            'code': 200,
            'data': []
        })
    
    houses = House.query.filter(House.number.like(f'%{query}%')).all()
    
    return jsonify({
        'code': 200,
        'data': [house.to_dict() for house in houses]
    }) 