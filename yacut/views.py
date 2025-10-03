import asyncio
import urllib.parse
from typing import Iterable, List, Tuple

import aiohttp
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    url_for
)


from . import db
from .forms import FileUploadForm, URLForm
from .models import URLMap
from .utils import get_unique_short_id

API_HOST = 'https://cloud-api.yandex.net'
API_VERSION = 'v1'


index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    short_url = None
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = (
            form.custom_id.data.strip()
            if form.custom_id.data else None
        )

        if custom_id and custom_id.lower() == 'files':
            flash('Предложенный вариант короткой ссылки уже существует.')
        else:
            if custom_id:
                if URLMap.query.filter_by(short=custom_id).first():
                    flash(
                        'Предложенный вариант короткой ссылки уже существует.')
                else:
                    url_map_obj = URLMap(original=original, short=custom_id)
                    db.session.add(url_map_obj)
                    db.session.commit()
                    short_url = url_for('index_bp.redirect_short',
                                        short=custom_id, _external=True)
            else:
                generated_id = get_unique_short_id()
                url_map_obj = URLMap(original=original, short=generated_id)
                db.session.add(url_map_obj)
                db.session.commit()
                short_url = url_for('index_bp.redirect_short',
                                    short=generated_id, _external=True)

    return render_template('index.html', form=form, short_url=short_url)


@index_bp.route('/<string:short>')
def redirect_short(short: str):
    url_map_obj = URLMap.query.filter_by(short=short).first_or_404()
    return redirect(url_map_obj.original)


@index_bp.route('/files', methods=['GET', 'POST'])
def upload_files():
    form = FileUploadForm()
    uploaded_files: List[Tuple[str, str]] = []
    if form.validate_on_submit():
        files: Iterable = form.files.data

        async def process_files(file_storage_list):
            request_upload_url = (
                f'{API_HOST}/{API_VERSION}/disk/resources/upload'
            )
            download_link_url = (
                f'{API_HOST}/{API_VERSION}/disk/resources/download'
            )

            token = current_app.config.get('DISK_TOKEN')
            if not token:
                raise RuntimeError('DISK_TOKEN is not configured')
            auth_headers = {'Authorization': f'OAuth {token}'}

            results: List[Tuple[str, str]] = []
            async with aiohttp.ClientSession() as session:
                for storage in file_storage_list:
                    filename = storage.filename
                    file_bytes = storage.read()

                    params = {'path': f'app:/{filename}', 'overwrite': 'true'}
                    async with session.get(
                        request_upload_url,
                        headers=auth_headers,
                        params=params
                    ) as resp:
                        data = await resp.json()
                        upload_href = data.get('href')

                    async with aiohttp.ClientSession() as upload_session:
                        async with upload_session.put(
                            upload_href,
                            data=file_bytes
                        ) as upload_resp:
                            location = upload_resp.headers.get('Location')

                    path_on_disk = urllib.parse.unquote(location).replace(
                        '/disk', '')

                    async with session.get(
                        download_link_url,
                        headers=auth_headers,
                        params={'path': path_on_disk}
                    ) as dl_resp:
                        dl_data = await dl_resp.json()
                        direct_link = dl_data.get('href')

                    results.append((filename, direct_link))
            return results

        try:
            direct_links = asyncio.run(process_files(files))
        except Exception as exc:
            flash(f'Произошла ошибка при загрузке файлов: {exc}')
        else:
            for filename, direct_link in direct_links:
                short_id = get_unique_short_id()
                url_map_obj = URLMap(original=direct_link, short=short_id)
                db.session.add(url_map_obj)
                uploaded_files.append((filename, url_for(
                    'index_bp.redirect_short',
                    short=short_id, _external=True)))
            db.session.commit()
    return render_template('files.html', form=form,
                           uploaded_files=uploaded_files)
