from . import db
from datetime import datetime

class RepairWorker(db.Model):
    __tablename__ = 'repair_workers'
    #维修工人：工号，姓名，性别，年龄，电话，工作状态
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), nullable=False, unique=True, comment='工号')
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    worktype=db.Column(db.String(20),nullable=False,comment='工种')
    phone = db.Column(db.String(20), nullable=False, comment='电话')
    address=db.Column(db.String(80),nullable=False,comment='地址')
    # 关联关系
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'name': self.name,
            'worktype': self.worktype,
            'phone': self.phone,
            'address':self.address
       } 