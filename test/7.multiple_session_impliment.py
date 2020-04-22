import subprocess

from selenium.webdriver import Chrome

import pywebio
import template
import util, time
from pywebio.input import *
from pywebio.output import *
from pywebio.utils import to_coroutine, run_as_function


def target():
    set_auto_scroll_bottom(True)

    template.basic_output()

    template.background_output()

    run_as_function(template.basic_input())

    actions(buttons=['Continue'])

    template.background_input()


async def async_target():
    set_auto_scroll_bottom(True)

    template.basic_output()

    await template.coro_background_output()

    await to_coroutine(template.basic_input())

    await actions(buttons=['Continue'])

    await template.coro_background_input()


def test(server_proc: subprocess.Popen, browser: Chrome):
    template.test_output(browser, percy_prefix='[multi tornado coro]')

    time.sleep(1)

    template.test_input(browser, percy_prefix='[multi tornado coro]')

    time.sleep(3)

    browser.get('http://localhost:8080?_pywebio_debug=1&pywebio_api=io2')

    template.test_output(browser, percy_prefix='[multi tornado thread]')

    time.sleep(1)

    template.test_input(browser, percy_prefix='[multi tornado thread]')


def start_test_server():
    pywebio.enable_debug()

    import tornado.ioloop
    import tornado.web
    from pywebio.platform.tornado import webio_handler
    from pywebio import STATIC_PATH

    application = tornado.web.Application([
        (r"/io", webio_handler(async_target)),
        (r"/io2", webio_handler(target)),
        (r"/(.*)", tornado.web.StaticFileHandler,
         {"path": STATIC_PATH, 'default_filename': 'index.html'})
    ])
    application.listen(port=8080, address='localhost')
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    util.run_test(start_test_server, test)