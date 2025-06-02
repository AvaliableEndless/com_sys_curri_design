from . import db
from datetime import datetime

class Purchase(db.Model):
    __tablename__ = 'purchase'
    #购买单：购买日期，购买业主id，房子型号，缴费方式，缴费金额，欠款数量，使用状况
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.number'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('house.number'), nullable=False)
    payment_method = db.Column(db.String(50))
    paid_amount = db.Column(db.Numeric(10, 2), default=0)
    debt_amount = db.Column(db.Numeric(10, 2), default=0)
    usage_status = db.Column(db.String(20))  # 使用状况
    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'house_id': self.house_id,
            'payment_method': self.payment_method,
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0,
            'debt_amount': float(self.debt_amount) if self.debt_amount else 0,
            'usage_status': self.usage_status,
        } 