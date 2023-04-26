import os
import json
import logging
import subprocess
from multiprocessing import Process

from bottle import run, get, request, response


ARCHIVEBOX_BIN = os.getenv('ARCHIVEBOX_BIN') or '/usr/bin/archivebox'
CURSED_PORT = os.getenv('CURSED_PORT') or 9998
CURSED_HOST = os.getenv('CURSED_HOST') or '0.0.0.0'
CURSED_SERVER = os.getenv('CURSED_SERVER') or 'gunicorn'


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s"
)


def shell_exec(command: list, to_stdin: str = None) -> None:
    """Execute shell command and return output."""
    pipe = subprocess.Popen(command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    if to_stdin:
        to_stdin = '%s\n' % to_stdin
        pipe.stdin.write(to_stdin.encode('utf-8'))
        pipe.stdin.flush()
    output, error = pipe.communicate()
    output = output.strip().decode("utf-8")
    error = error.decode("utf-8")
    if pipe.returncode != 0:
        raise RuntimeError(error)
    return output


def run_bg_task(cmd):
    logging.debug('PID=%s Run "background" thread...', os.getpid())
    shell_exec(cmd)
    logging.debug('PID=%s Background thread finished', os.getpid())


@get('/add')
def add_to_archive() -> str:
    response.set_header('Content-Type', 'application/json')
    url = request.query.url or None
    depth = request.query.depth or None
    tag = request.query.tag or None
    cmd = ARCHIVEBOX_BIN.split()
    cmd.append("add")
    if depth:
        cmd.append('--depth=' + str(depth))
    if tag:
        cmd.append('--tag=' + tag)
    if url is None:
        response.status = 400
        return json.dumps({'msg': 'Error: No URL query parameter provided'})
    cmd.append("'" + url + "'")
    logging.debug('PID=%s Command to run: %s', os.getpid(), cmd)
    taskrun = Process(target=run_bg_task, args=(cmd,))
    taskrun.start()
    return json.dumps({'msg': 'OK'})


run(server=CURSED_SERVER, host=CURSED_HOST, port=CURSED_PORT)
