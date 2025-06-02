from . import db
from datetime import datetime

class PaymentBill(db.Model):
    __tablename__ = 'payment_bills'
    #缴费单：缴费单号，缴费房屋，缴费人编号，缴费类型，金额，描述，是否缴费，缴费方式
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.number'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.number'), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # 缴费类型
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # 金额
    description = db.Column(db.String(200))  # 描述
    status = db.Column(db.String(20), default='unpaid')  # 状态：unpaid, paid, cancelled
    pay_way = db.Column(db.String(100),default='cash')  # 缴费方式

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'house_id':self.house_id,
            'type': self.type,
            'amount': float(self.amount) if self.amount else 0,
            'description': self.description,
            'status': self.status,
            'pay_way': self.pay_way,
        } 