# Use whiptail to display dialog boxes from shell scripts
# Copyright (C) 2022 Alessandro Piroddi
# Copyright (C) 2013 Marwan Alsabbagh
# license: BSD, see LICENSE for more details.

from __future__ import print_function

import itertools
import logging
import math
import shlex
import sys
from collections import namedtuple
from subprocess import Popen, PIPE

__version__ = '0.4'
PY3 = sys.version_info[0] == 3
string_types = str if PY3 else basestring
Response = namedtuple('Response', 'returncode value')

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def flatten(data):
    return list(itertools.chain.from_iterable(data))


class Whiptail(object):
    def __init__(self, title='', backtitle='', height=10, width=50,
                 auto_exit=True, debug=False):
        self.title = title
        self.backtitle = backtitle
        self.height = height
        self.width = width
        self.auto_exit = auto_exit
        self.log = logger

        if debug:
            self.log.setLevel(logging.DEBUG)

    def __run(self, control, msg, extra=(), exit_on=(1, 255)):
        cmd = [
            'whiptail', '--title', self.title, '--backtitle', self.backtitle,
            '--' + control, msg, str(self.height), str(self.width)
        ]
        if any(extra):
            cmd += list(extra)

        self.log.debug(" ".join(cmd))

        p = Popen(cmd, stderr=PIPE)
        out, err = p.communicate()
        self.log.debug('Return code: {}'.format(p.returncode))
        if self.auto_exit and p.returncode in exit_on:
            self.log.info('User cancelled operation.')
            sys.exit(p.returncode)
        return Response(p.returncode, err)

    @staticmethod
    def __fix_return_value(ret_value):
        if PY3:
            if type(ret_value) not in (float, int):
                return ret_value.decode("utf-8")
            else:
                return ret_value
        else:
            return ret_value

    def inputbox(self, msg, default=''):
        ret_value = self.__run('inputbox', msg, extra=[default]).value
        return self.__fix_return_value(ret_value)

    def passwordbox(self, msg, default=''):
        ret_value = self.__run('passwordbox', msg, extra=[default]).value
        return self.__fix_return_value(ret_value)

    def yesno(self, msg, default='yes'):
        defaultno = '--defaultno' if default == 'no' else ''
        return self.__run('yesno', msg, extra=[defaultno], exit_on=[255]).returncode == 0

    def msgbox(self, msg):
        self.__run('msgbox', msg)

    def textbox(self, path):
        self.__run('textbox', path, extra=['--scrolltext'])

    def _calc_height(self, msg, items):
        msg_height = 0
        if msg:
            msg_height = int(math.ceil(len(msg) / float(self.width)))

        minimum_height = msg_height + 7
        optimal_height = len(items)
        remaining_height = self.height - minimum_height
        if optimal_height > remaining_height:
            return [str(remaining_height)]
        else:
            return [str(optimal_height)]

    def menu(self, msg='', items=(), prefix=' - '):
        if isinstance(items[0], string_types):
            items = [(i, '') for i in items]
        else:
            items = [(k, prefix + v) for k, v in items]
        extra = [str(len(items))] + flatten(items)
        return self.__fix_return_value(self.__run('menu', msg, extra).value)

    def __show_list(self, control, msg, items, prefix, defaults):
        if defaults is None or len(items) != len(defaults):
            defaults = ['OFF' for _ in items]
        else:
            defaults = ['ON' if _ else 'OFF' for _ in defaults]
        if isinstance(items[0], str):
            items = [(item, '', defaults[idx]) for idx, item in enumerate(items)]
        else:
            items = [(k, prefix + v, s) for k, v, s in items]
        extra = self._calc_height(msg, items) + flatten(items)
        ret = self.__fix_return_value(self.__run(control, msg, extra).value)
        return shlex.split(ret)

    def radiolist(self, msg='', items=(), prefix='', defaults=None):
        return self.__show_list('radiolist', msg, items, prefix, defaults)

    def checklist(self, msg='', items=(), prefix='', defaults=None):
        return self.__show_list('checklist', msg, items, prefix, defaults)
