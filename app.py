from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from db import User, Currency, Currency_info, db, app
from functools import wraps
import datetime
import methods
import uuid
import jwt




page_url = 'https://finance.naver.com/marketindex/worldExchangeList.nhn?key=exchange&page='


pages = methods.page(page_url)




def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing', 'Next': 'You need to login again and get new token', 'then': 'Try again' }), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!', 'Next': 'You need to login again and get new token', 'then': 'Try again' }), 401

        return f(current_user, *args, **kwargs)

    return decorated



@app.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()

    username = data['username']
    hashed_password = generate_password_hash(data['password'], method='sha256')

    user = User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify({'message': f"the username {username} already exist", "Next": "Please try another one for your username"})

    new_user = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New User created'})




@app.route('/login', methods=['GET'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not veryify', 401, {'WWW_Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response('Could not veryify', 401, {'WWW_Authenticate': 'Basic realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not veryify', 401, {'WWW_Authenticate': 'Basic realm="Login required!"'})





@app.route('/mw_finance/user_del', methods=['DELETE'])
def delete_user():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Please enter your username or password perfectly'})

    user = User.query.filter_by(username=auth.username).first()

    if not user:
        return jsonify({'message': 'Please check your username'})
    if check_password_hash(user.password, auth.password):
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'})
    return jsonify({'message': 'Please check your password'})





@app.route('/mw_finance', methods=['GET'])
@token_required
def home(current_user):
    if not current_user.username:
        return jsonify({'message' : 'Something went wrong'})
    menu = Currency.query.all()
    result = {"* Instruction *": "You can get the information that you want by enterting this address => http://127.0.0.1:5000/mw_finance/**the number**"}

    for one in menu:
        result[f"{one.name}"] = f"{one.id}"
    return jsonify(result)




@app.route('/mw_finance/<currency_id>', methods=['GET'])
@token_required
def search(current_user, currency_id):
    if not current_user.username:
        return jsonify({'message' : 'Something went wrong'})

    currency_id = int(currency_id)

    if currency_id == 1:
        currency_infos = Currency_info.query.all()
        if len(currency_infos) != 0:
            return methods.case_currency_id_1_and_len_num(pages)
        else:
            return methods.case_currency_id_1_and_len_zero(pages)
    else:
        return methods.case_currency_id_not_1(currency_id, pages)






if __name__ == '__main__':
    app.run(debug=True)
















