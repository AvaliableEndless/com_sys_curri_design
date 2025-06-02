from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from extension import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化扩展
    CORS(app)
    db.init_app(app)
    with app.app_context():
        # 注册蓝图
    
        from routes.owner import owner_bp
        from routes.house import house_bp
        from routes.payment import payment_bp
        from routes.violation import violation_bp
        from routes.complaint import complaint_bp
        from routes.repair import repair_bp
        from routes.worker import worker_bp
        
        
        app.register_blueprint(owner_bp, url_prefix='/api/owners')
        app.register_blueprint(house_bp, url_prefix='/api/houses')
        app.register_blueprint(payment_bp, url_prefix='/api/payment-bills')
        app.register_blueprint(violation_bp, url_prefix='/api/violation-bills')
        app.register_blueprint(complaint_bp, url_prefix='/api/complaint-bills')
        app.register_blueprint(repair_bp, url_prefix='/api/repair-bills')
        app.register_blueprint(worker_bp, url_prefix='/api/repair_workers')

    
    # 错误处理
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'code': 404,
                'message': '接口不存在'
            }), 404

        @app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'code': 500,
                'message': '服务器内部错误'
            }), 500

    return app

if __name__ == '__main__':
    app = create_app()
    
    # 创建所有数据库表
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5000) 