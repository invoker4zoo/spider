# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechart: whatshowlove
@ software: PyCharm
@ file: deploy.py
@ time: $17-7-26 下午3:06
"""
from fabric.api import *
from fabric.contrib.files import exists

BASE_PATH = '/usr/app/python/'
TAR_FILE = 'weibo_crawler.tar.gz'
APP_PATH = BASE_PATH + 'weibo_crawler'

# not final running app,for test
APP_NAME = 'dispatch.py'


def tar_codes():
    with settings(warn_only=True):
        local("virtualenv yjl_env && source yjl_env/bin/activate && pip install -r requirements.txt", shell='/bin/bash')
        local("rm */*.pyc", shell='/bin/bash')
        local("tar -zcf {fname} *".format(fname=TAR_FILE), shell='/bin/bash')


def deploy_app():
    if not exists(APP_PATH):
        run('mkdir -p ' + APP_PATH)
    with settings(warn_only=True):
        sudo('rm -Rf ' + APP_PATH + '/*')
    put(TAR_FILE, APP_PATH + '/')
    with cd(APP_PATH):
        run('tar -zxf ' + TAR_FILE, shell='/bin/bash')
        run('rm ' + TAR_FILE, shell='/bin/bash')


def run_app():
    with settings(warn_only=True):
        sudo('pkill -f ' + APP_NAME)
    with cd(APP_PATH):
        run('sleep 2')
        run('source yjl_env/bin/activate && $(nohup python {app} >& /dev/null < /dev/null &) && sleep 1'.format(
            app=APP_NAME), shell='/bin/bash')


def kill():
    with settings(warn_only=True):
        run('pkill -f ' + APP_NAME)


@parallel(pool_size=4)
def install_package():
    # sudo('apt-get -y update')
    sudo('apt-get -y install libpq-dev')
    sudo('pip install psycopg2')


if __name__ == "__main__":
    """ deploy test ,

    just push file
    test path : /usr/app/python/crawler-api-test
    """
    env.hosts = [
        "root@192.168.45.140",
        #"root@192.168.45.144",
        #"root@192.168.45.145",
        #"root@192.168.45.146",
    ]
    env.password = 'RryW8psav=f8'
    tar_codes()
    APP_PATH = APP_PATH + '_test'
    execute(deploy_app)
    execute(run_app)
    #execute(install_package)