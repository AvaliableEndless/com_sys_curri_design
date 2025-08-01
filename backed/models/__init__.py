from flask_sqlalchemy import SQLAlchemy
from app import db


def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

# 导入所有模型
from models.owners import Owner
from models.house import House
from models.payment_bills import PaymentBill
from models.violation_bills import ViolationBill
from models.complaint_bills import ComplaintBill
from models.repair_bills import RepairBill
from models.repair_worker import RepairWorker

__all__ = [
    'Owner',
    'House',
    'PaymentBill',
    'ViolationBill',
    'ComplaintBill',
    'RepairBill',
    'RepairWorker'
] 