from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import (DataRequired, Length, Optional, Regexp,
                                URL)


class URLForm(FlaskForm):

    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(require_tld=False, message='Некорректная ссылка'),
        ],
    )
    custom_id = StringField(
        'Короткая ссылка',
        validators=[
            Length(
                max=16,
                message=(
                    'Длина короткой ссылки '
                    'не должна превышать 16 символов'
                )
            ),
            Optional(),
            Regexp(
                r'^[A-Za-z0-9]*$',
                message='Указано недопустимое имя для короткой ссылки'
            ),
        ],
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):

    files = MultipleFileField(
        'Выберите файлы',
        validators=[
            DataRequired(message='Необходимо выбрать хотя бы один файл'),
        ],
    )
    submit = SubmitField('Загрузить')