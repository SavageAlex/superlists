# from fabric.contrib.files import append, exists, sed
# from fabric.api import env, local, run
# import random
from fabric import Connection
from fabric.tasks import task
from patchwork.files import exists, append
import random

# env.key_filename = '/home/alex/.ssh/ec2key.pem'
# SERVER_KEY = '/home/alex/.ssh/ec2key.pem'
REPO_URL = 'https://github.com/SavageAlex/superlists.git'

def _create_directory_structure_if_necessary(c, site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        c.run(f'mkdir -p {site_folder}/{subfolder}')

def _get_latest_source(c, source_folder):
    if exists(c, source_folder + '/.git'):
        c.run(f'cd {source_folder} && git fetch')
    else:
        c.run(f'git clone {REPO_URL} {source_folder}')
    current_commit = c.local("git log -n 1 --format=%H") # current_commit = c.local("git log -n 1 --format=%H", capture=True)
    c.run(f'cd {source_folder} && git reset --hard {current_commit}')

def _update_settings(c, source_folder, site_name):
    settings_path = source_folder + '/superlists/settings.py'
    c.run(f'sed "s/DEBUG = True/DEBUG = False/g" {settings_path}')     # (settings_path, "DEBUG = True", "DEBUG = False") changed for: 'sed -i<backup> -r -e "/<limit>/ s/<before>/<after>/<flags>g" <filename>'
    c.run(f'sed "s/ALLOWED_HOSTS =.+$/ALLOWED_HOSTS = ["{site_name}"]/g" {settings_path}')      # settings_path, 'ALLOWED_HOSTS =.+$', f'ALLOWED_HOSTS = ["{site_name}"]'
    secret_key_file = source_folder + '/superlists/secret_key.py'
    if not exists(c, secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(c, secret_key_file, f'SECRET_KEY = "{key}"')
    append(c, settings_path, '\nfrom .secret_key import SECRET_KEY') # new line /n returns None

def _update_virtualenv(c, source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(c, virtualenv_folder + '/bin/pip'):
        c.run(f'python3.8 -m venv {virtualenv_folder}')
    c.run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')

def _update_static_files(c, source_folder):
    c.run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py collectstatic --noinput'
    )

def _update_database(c, source_folder):
    c.run(
        f'cd {source_folder}'
        ' && ../virtualenv/bin/python manage.py migrate --noinput'
    )

@task
def deploy(ctx):
    with Connection(ctx.host, connect_timeout=10, ) as conn:

        site_folder = f'/home/{conn.user}/sites/{conn.host}'
        source_folder = site_folder + '/source'
        _create_directory_structure_if_necessary(conn, site_folder)
        _get_latest_source(conn, source_folder)
        _update_settings(conn, source_folder, conn.host)
        _update_virtualenv(conn, source_folder)
        _update_static_files(conn, source_folder)
        _update_database(conn, source_folder)