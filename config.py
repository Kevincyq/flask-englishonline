import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:Seucyq19801007@localhost:3306/flaskr'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 5
    COURSES_PER_PAGE = 20
    SESSION_PER_PAGE = 20
    LANGUAGES = ['en', 'zh']
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #MAIL_SERVER = ['smtp.googlemail.com']
    #MAIL_PORT = ['587']
    #MAIL_USE_TLS = 1
    #MAIL_USERNAME = ['kevincyq@gmail.com']
    #MAIL_PASSWORD = ['Seucyq_80100h']
    ADMINS = ['1322056230@qq.com']
    '''JOBS=[
        {
            'id': 'job1',
            'func': 'flaskr.cousession:set_status',
            'trigger': 'cron',
            'hour': 16,
            'minute': 18,
        }
        #{
        #    'id': 'job2',
        #    'func': 'flaskr.__init__:job_1',
        #    'args': (3,4),
        #    'trigger': 'interval',
        #    'seconds': 5
        #}
    ]'''

