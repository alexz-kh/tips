#!/usr/bin/python

import sys, os, time, re, copy
import subprocess, six, shlex
import logging as LOG
import yaml

LOG.basicConfig(level=LOG.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)-15s - [%(levelname)s] %(module)s:%(lineno)d: '
                       '%(message)s', )


# copy-paste from openstack/fuel-agent project

class BaseError(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(BaseError, self).__init__(message, *args, **kwargs)


class ProcessExecutionError(BaseError):
    def __init__(self, stdout=None, stderr=None, exit_code=None, cmd=None,
                 description=None):
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout
        self.cmd = cmd
        self.description = description

        if description is None:
            description = ("Unexpected error while running command.")
        if exit_code is None:
            exit_code = '-'
        message = ('%(description)s\n'
                   'Command: %(cmd)s\n'
                   'Exit code: %(exit_code)s\n'
                   'Stdout: %(stdout)r\n'
                   'Stderr: %(stderr)r') % {'description': description,
                                            'cmd': cmd,
                                            'exit_code': exit_code,
                                            'stdout': stdout,
                                            'stderr': stderr}
        super(ProcessExecutionError, self).__init__(message)


def execute(*cmd, **kwargs):
    command = ' '.join(cmd)
    LOG.debug('Trying to execute command: %s', command)
    commands = [c.strip() for c in re.split(r'\|', command)]
    if kwargs.get('env_variables'):
        LOG.debug('Env variables: {0}'.
                  format(kwargs.get('env_variables')))
    env = kwargs.pop('env_variables', copy.deepcopy(os.environ))
    env['PATH'] = '/bin:/usr/bin:/sbin:/usr/sbin'
    env['LC_ALL'] = env['LANG'] = env['LANGUAGE'] = kwargs.pop('language',
                                                               'C')
    attempts = kwargs.pop('attempts', 1)
    check_exit_code = kwargs.pop('check_exit_code', [0])
    ignore_exit_code = False
    to_filename = kwargs.get('to_filename')
    cwd = kwargs.get('cwd')
    logged = kwargs.pop('logged', False)

    if isinstance(check_exit_code, bool):
        ignore_exit_code = not check_exit_code
        check_exit_code = [0]
    elif isinstance(check_exit_code, int):
        check_exit_code = [check_exit_code]

    to_file = None
    if to_filename:
        to_file = open(to_filename, 'wb')

    for attempt in reversed(six.moves.range(attempts)):
        try:
            process = []
            for c in commands:
                try:
                    # NOTE(eli): Python's shlex implementation doesn't like
                    # unicode. We have to convert to ascii before shlex'ing
                    # the command. http://bugs.python.org/issue6988
                    encoded_command = c.encode('ascii') if six.PY2 else c
                    process.append(subprocess.Popen(
                        shlex.split(encoded_command),
                        env=env,
                        stdin=(process[-1].stdout if process else None),
                        stdout=(to_file
                                if ((len(process) == len(commands) - 1) and
                                    to_file)
                                else subprocess.PIPE),
                        stderr=(subprocess.PIPE),
                        cwd=cwd
                    ))
                except (OSError, ValueError) as e:
                    raise ProcessExecutionError(exit_code=1,
                                                       stdout='',
                                                       stderr=e,
                                                       cmd=command)
                if len(process) >= 2:
                    process[-2].stdout.close()
            stdout, stderr = process[-1].communicate()
            if (not ignore_exit_code and
                        process[-1].returncode not in check_exit_code):
                raise ProcessExecutionError(
                    exit_code=process[-1].returncode, stdout=stdout,
                    stderr=stderr, cmd=command)
            if logged:
                LOG.debug('Extended log: \nstdout:{0}\nstderr:{1}'.
                          format(stdout, stderr))
            return (stdout, stderr)
        except ProcessExecutionError as e:
            LOG.warning('Failed to execute command: %s', e)
            if not attempt:
                raise
            else:
                time.sleep(10)
# end of copy-paste

def read_file(text_file):
  if not os.path.isfile(text_file):
    LOG.error("File not exist:{}".format(text_file))
    sys.exit(1)
  with open(text_file, 'r') as f:
    x = f.read().split('\n')
  return x

def read_yaml(y_file):
    data = {}
    if os.path.exists(y_file):
        with open(y_file) as f:
            data = yaml.safe_load(f)
            return data
    else:
        LOG.error("File couldn't be found: {0}"
                  .format(y_file))
    sys.exit(1)

def save_yaml(save_yaml, to_file):
  if not os.path.exists(os.path.dirname(to_file)):
    try:
      os.makedirs(os.path.dirname(to_file))
    except OSError as exc:
      LOG.error("Unable create:{}".format(to_file))
      sys.exit(1)
  with open(to_file, 'w') as f:
    f.write(yaml.dump(save_yaml, default_flow_style=False))
    LOG.info("{} file saved".format(to_file))

def list_get (l, idx, default=None):
  try:
    return l[idx]
  except IndexError:
    LOG.error("No such index:{}\nReturning default:{}".format(idx,default))
    return default

def str2bool(v):
  if type(v) == bool:
    return v
  return v.lower() in ("yes", "true", "y", "1")

def dict_merge(a, b):
    """ Recursively merges dict's.

    Not just simple a['key'] = b['key'], if both a and b have a key
    who's value is a dict then dict_merge is called on both values
    and the result stored in the returned dictionary.
    """
    if not isinstance(b, dict):
        return copy.deepcopy(b)
    result = copy.deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result
