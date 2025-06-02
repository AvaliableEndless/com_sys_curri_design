from . import db
from datetime import datetime

# 业主-房屋关系表
owner_houses = db.Table('owner_houses',
    db.Column('owner_number', db.Integer, db.ForeignKey('owners.number'), primary_key=True),
    db.Column('house_number', db.Integer, db.ForeignKey('houses.number'), primary_key=True)
)

class Owner(db.Model):
    """业主模型"""
    __tablename__ = 'owners'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True, comment='业主编号')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    gender = db.Column(db.String(10), nullable=False, comment='性别')
    age = db.Column(db.Integer)
    phone = db.Column(db.String(11), unique=True, nullable=False, comment='联系电话')
    id_card = db.Column(db.String(18), unique=True, nullable=False, comment='身份证号')
    # 关联关系
    #这是一个多对多关系（业主和房屋），中间通过 owner_houses 表桥接
    #backref='owners' 表示可以通过 house.owners 得到住在这栋房子里的所有业主
    #lazy='subquery' 表示访问 owner.houses 时会使用子查询优化性能
    houses = db.relationship('House', secondary=owner_houses, lazy='subquery',
        backref=db.backref('owners', lazy=True))
    #一对多：一个业主有多个缴费单
    payment_bills = db.relationship('PaymentBill', backref='owner', lazy='dynamic')
    #一对多：一个业主有多个违章单
    violation_bills = db.relationship('ViolationBill', backref='owner', lazy='dynamic')
    #一对多：一个业主有多个投诉单
    complaint_bills = db.relationship('ComplaintBill', backref='owner', lazy='dynamic')
    #一对多：一个业主有多个保修单
    repair_bills = db.relationship('RepairBill', backref='owner', lazy='dynamic')
    
    def __repr__(self):
        return f'<Owner {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'id_card': self.id_card,
        } 