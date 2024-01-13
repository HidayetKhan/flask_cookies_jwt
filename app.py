from flask import Flask,jsonify,request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, set_access_cookies, get_jwt_identity
from flask_restful import Api,Resource
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app=Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db=SQLAlchemy(app)
api=Api(app)
jwt=JWTManager(app)


class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(200))
    password=db.Column(db.String(200))



class UserRegistration(Resource):
    def post(self):
        data=request.get_json()
        username=data['username']
        password=data['password']
        if not username and not password:
            return jsonify({'message':'username and password are invalid'}),400
        if User.query.filter_by(username=username).first():
            return jsonify({'message':'user all redy exsist'})
        new_user=User(username=username,password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message':'new user created sucssefully'}),200

from flask_jwt_extended import create_access_token, set_access_cookies

class UserLogin(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            user = User.query.filter_by(username=username).first()

            if user and user.password == password:
                access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
                response = jsonify({'login': True})
                set_access_cookies(response, access_token)
                return response, 200
            else:
                return jsonify({'login': False, 'message': 'Invalid credentials'}), 401
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

class UserProtected(Resource):
    @jwt_required()
    def get(self):
        try:
            current_user = get_jwt_identity()
            response_data = {'message': f'Hello {current_user}, your resource is protected'}
            return jsonify(response_data), 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500


api.add_resource(UserRegistration,'/register')
api.add_resource(UserLogin,'/login')
api.add_resource(UserProtected,'/protect')

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)

