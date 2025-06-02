from . import db
from datetime import datetime

class House(db.Model):
    __tablename__ = 'houses'
    #房屋：编号，房型，面积，使用面积
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True, comment='房屋编号')
    area = db.Column(db.Float, nullable=False)
    using_area = db.Column(db.Float, nullable=False)
    house_type = db.Column(db.String(50), nullable=False)  # 一室一厅、两室一厅等

    # 关联关系
    payment_bills = db.relationship('PaymentBill', backref='house', lazy='dynamic')
    violation_bills = db.relationship('ViolationBill', backref='house', lazy='dynamic')
    complaint_bills = db.relationship('ComplaintBill', backref='house', lazy='dynamic')
    repair_bills = db.relationship('RepairBill', backref='house', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'area': self.area,
            'using_area': self.using_area,
            'house_type': self.house_type,
        } 
        