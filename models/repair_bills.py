from . import db
from datetime import datetime

class RepairBill(db.Model):
    __tablename__ = 'repair_bills'
    #维修单：维修单号，报修人，保修房屋，维修内容，维修日期，完成日期，费用，经办人
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)  # 保修业主
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)  # 保修房屋
    content = db.Column(db.Text, nullable=False)  # 维修内容
    repair_date = db.Column(db.DateTime, nullable=False)  # 维修日期
    finish_date = db.Column(db.DateTime)  # 完成日期
    cost = db.Column(db.Numeric(10, 2), default=0)  # 维修费用
    worker_id = db.Column(db.Integer, db.ForeignKey('repair_workers.id'), nullable=False)  # 维修工人

    # 关联关系

    worker = db.relationship('RepairWorker', backref=db.backref('repair_bills', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'house_id':self.house_id,
            'content': self.content,
            'repair_date': self.repair_date.isoformat() if self.repair_date else None,
            'finish_date': self.finish_date.isoformat() if self.finish_date else None,
            'cost': float(self.cost) if self.cost else 0,
            'worker_id': self.worker_id
        } 