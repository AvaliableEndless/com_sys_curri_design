from . import db
from datetime import datetime

# 业主-房屋关系表
owner_houses = db.Table('owner_houses',
    db.Column('owner_number', db.Integer, db.ForeignKey('owners.number', ondelete='CASCADE'), primary_key=True),
    db.Column('house_number', db.Integer, db.ForeignKey('houses.number', ondelete='CASCADE'), primary_key=True)
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
    houses = db.relationship('House', 
        secondary=owner_houses,
        primaryjoin="Owner.number==owner_houses.c.owner_number",
        secondaryjoin="House.number==owner_houses.c.house_number",
        lazy='subquery',
        backref=db.backref('owners', lazy=True))
    
    # 一对多关系
    payment_bills = db.relationship('PaymentBill', backref='owner', lazy='dynamic')
    violation_bills = db.relationship('ViolationBill', backref='owner', lazy='dynamic')
    complaint_bills = db.relationship('ComplaintBill', backref='owner', lazy='dynamic')
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
            'houses': [house.to_dict() for house in self.houses]
        } 