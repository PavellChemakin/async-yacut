import re
from http import HTTPStatus
from flask import Blueprint, jsonify, request, url_for

from .models import URLMap
from .utils import get_unique_short_id
from . import db


api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

VALID_CUSTOM_ID = re.compile(r'^[A-Za-z0-9]{1,16}$')


def is_valid_custom_id(custom_id: str) -> bool:
    return bool(VALID_CUSTOM_ID.match(custom_id))


@api_bp.route('/id/', methods=['POST'])
def create_short_id():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            'message': 'Отсутствует тело запроса'
        }), HTTPStatus.BAD_REQUEST

    original = data.get('url')
    if not original:
        return jsonify({
            'message': '"url" является обязательным полем!'
        }), HTTPStatus.BAD_REQUEST

    custom_id = data.get('custom_id')
    if custom_id is not None:
        custom_id = str(custom_id).strip()
        if not custom_id:
            custom_id = None

    if custom_id:
        if custom_id.lower() == 'files':
            return jsonify({
                'message': (
                    'Предложенный вариант короткой '
                    'ссылки уже существует.'
                )
            }), HTTPStatus.BAD_REQUEST
        if not is_valid_custom_id(custom_id):
            return jsonify({
                'message': 'Указано недопустимое имя '
                'для короткой ссылки'
            }), HTTPStatus.BAD_REQUEST
        if URLMap.query.filter_by(short=custom_id).first():
            return (
                jsonify({
                    'message': (
                        'Предложенный вариант короткой '
                        'ссылки уже существует.'
                    )
                }),
                HTTPStatus.BAD_REQUEST
            )
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    url_map_obj = URLMap(original=original, short=short_id)
    db.session.add(url_map_obj)
    db.session.commit()

    short_link = url_for('index_bp.redirect_short',
                         short=short_id, _external=True)
    return jsonify(
        {'url': original, 'short_link': short_link}), HTTPStatus.CREATED


@api_bp.route('/id/<string:short_id>/', methods=['GET'])
def get_original(short_id: str):
    url_map_obj = URLMap.query.filter_by(short=short_id).first()
    if not url_map_obj:
        return jsonify(
            {'message': 'Указанный id не найден'}), HTTPStatus.NOT_FOUND
    return jsonify({'url': url_map_obj.original}), HTTPStatus.OK
