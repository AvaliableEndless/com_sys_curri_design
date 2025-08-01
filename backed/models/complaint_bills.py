from . import db
from datetime import datetime

class ComplaintBill(db.Model):
    __tablename__ = 'complaint_bills'
    #投诉单：投诉单id，投诉日期，投诉内容，处理日期，处理结果，经办人
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    complaint_date = db.Column(db.DateTime, nullable=False)  # 投诉日期
    content = db.Column(db.Text, nullable=False)  # 投诉内容
    processed_at = db.Column(db.DateTime)  # 处理时间
    process_result = db.Column(db.Text,default='未处理')  # 处理结果
    operator = db.Column(db.String(50))  # 经办人

    def to_dict(self):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'house_id':self.house_id,
            'complaint_date': self.complaint_date.isoformat() if self.complaint_date else None,
            'content': self.content,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'process_result': self.process_result,
            'operator': self.operator,
        } 