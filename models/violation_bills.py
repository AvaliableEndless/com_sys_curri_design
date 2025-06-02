from . import db
from datetime import datetime

class ViolationBill(db.Model):
    __tablename__ = 'violation_bills'
    #违规单：违规单号，违规人编号，违规房屋，违规类型，违规金额，是否交费，日期，收费人员
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.number'), nullable=False)#被违规对象
    house_id = db.Column(db.Integer, db.ForeignKey('houses.number'), nullable=False)#违规房屋
    type = db.Column(db.String(100), nullable=False)  # 违规类型
    fine_amount = db.Column(db.Numeric(10, 2), default=0)  # 罚款金额
    status = db.Column(db.String(20), default='pending')  # 状态：pending, processed, cancelled
    processed_at = db.Column(db.DateTime)  # 处理时间
    worker=db.Column(db.String(40),nullable=False)#处理人员
    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'house_id': self.house_id,
            'type': self.type,
            'fine_amount': float(self.fine_amount) if self.fine_amount else 0,
            'status': self.status,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'worker': self.worker,
            
        } 