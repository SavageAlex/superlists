from fabric import Connection

def _get_manage_dot_py(host):
    return f'~/sites/{host}/virtualenv/bin/python ~/sites/{host}/source/manage.py'

def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    with Connection(f'ubuntu@{host}') as c:
        c.run(f'{manage_dot_py} flush --noinput')

def create_session_on_server(host, email):
    manage_dot_py = _get_manage_dot_py(host)
    with Connection(f'ubuntu@{host}') as c:
        result = c.run(f'{manage_dot_py} create_session {email}')
        session_key = result.stdout
        return session_key.strip()