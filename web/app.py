# coding:utf-8
from __future__ import unicode_literals

import codecs
import datetime
from flask import Flask, url_for, redirect, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
import flask_admin as admin
import flask_login as login
from flask_babelex import Babel
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib.mongoengine import ModelView
from mongoengine import *
from jinja2 import Markup
from MediaLabelSpider.utils import PROJECT_ROOT


connect('MediaLabel', host='localhost', username='', password='')
# Create Flask application
app = Flask(__name__)

babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# Create user model.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username




# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

class MediaLabelData(Document):

    media_type = StringField(required=False, verbose_name='媒体类型')
    first_cate = StringField(default='', verbose_name='一级类目')
    second_cate = StringField(default='', verbose_name='二级类目')
    media_name = StringField(default='', verbose_name='媒体名称')
    url = StringField(default='', verbose_name='网站url')
    web_place = StringField(default='', verbose_name='网站地区')
    type = StringField(default='', verbose_name='网站类型')
    score = IntField(required=False, default=0,verbose_name='综合得分')
    link_num = IntField(required=False, default=0,verbose_name='反链数')
    baidu_pc_weight = IntField(required=False, default=0,verbose_name='百度pc权重')
    baidu_mobile_weight = IntField(required=False, default=0,verbose_name='百度mobile权重')
    desc = StringField(default='', verbose_name='网站简介')
    website_rank = StringField(default='', verbose_name='国内排名')
    province_rank = StringField(default='', verbose_name='省份排名')
    industry_rank = StringField(default='', verbose_name='网站行业类型排名')
    mobile_url = StringField(default='', verbose_name='移动url')
    company_name = StringField(default='', verbose_name='公司名称')
    representative = StringField(default='', verbose_name='法定代表人')
    registered_capital = StringField(default='', verbose_name='公司注册资本')
    registered_date = StringField(default='', verbose_name='注册时间')
    company_properties = StringField(default='', verbose_name='企业性质')
    ip_address = StringField(default='', verbose_name='ip地址')
    server_address = StringField(default='', verbose_name='服务器地址')
    domain = StringField(default='', verbose_name='域名')
    dm_server = StringField(default='', verbose_name='域名服务商')
    dm_create_time = StringField(default='', verbose_name='域名创建时间')
    dm_deadline = StringField(default='', verbose_name='域名到期时间')
    update_time = StringField(default='', verbose_name='数据更新日期')
    validated = BooleanField(default=False, verbose_name='网站验证是否有效')
    add_time = DateTimeField(
        db_field='createtime',
        default=datetime.datetime.now,
        verbose_name='创建时间',
    )

    meta = {
        'strict': False,
        'index_background': True,
        "collection": "media_label_data",
        "indexes": [
            "add_time",
        ]
    }


class MediaLabelDataStatistics(Document):
    """
    @summary: 媒体资源库
    """
    media_type = StringField(required=False, verbose_name='媒体类型')
    first_cate = StringField(default='', verbose_name='一级类目')
    second_cate = StringField(default='', verbose_name='二级类目')
    number = IntField(required=False, default=0,verbose_name='爬取数量')
    add_time = DateTimeField(
        db_field='createtime',
        default=datetime.datetime.now,
        verbose_name='创建时间',
    )

    meta = {
        'strict': False,
        'index_background': True,
        "collection": "MediaLabelDataStatistics",
        "indexes": [
            "first_cate",
            "second_cate",
            'number',
        ]
    }

    def __unicode__(self):

        return '%s %s %s %s %s' % \
               (self.media_type,
                self.first_cate,
                self.second_cate,
                self.number,
                self.add_time,
                )


class MediaLabelDataView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    column_list = ['media_type', 'first_cate', 'second_cate', 'media_name', 'url', 'web_place', 'type', 'score',
                   'link_num', 'baidu_pc_weight', 'baidu_mobile_weight', 'website_rank',
                   'province_rank', 'industry_rank', 'mobile_url', 'company_name', 'representative',
                   'registered_capital', 'registered_date', 'company_properties', 'ip_address', 'server_address',
                   'domain', 'dm_server', 'dm_create_time', 'dm_deadline', 'update_time', 'add_time']
    column_filters = ['first_cate', 'second_cate', 'media_name']
    column_searchable_list = ['first_cate', 'second_cate', 'media_name']
    column_sortable_list = ['add_time']
    column_default_sort = ('add_time', True)

    column_formatters = {
        'url': lambda v, c, m, p: Markup(
            "<a href=%s>%s</a>" % (m.url, str(m.url))),
        'mobile_url': lambda v, c, m, p: Markup(
            "<a href=%s>%s</a>" % (m.mobile_url, str(m.mobile_url))),
    }


class MediaLabelDataStatisticsView(ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    @expose('/')
    def index_view(self):
        """
            List view
        """
        self.list_template = 'bar.html'

        return super(MediaLabelDataStatisticsView, self).index_view()

    column_list = ['media_type', 'first_cate', 'second_cate', 'number', 'add_time']
    column_filters = ['media_type', 'first_cate', 'second_cate']
    column_searchable_list = ['first_cate', 'second_cate']
    column_sortable_list = ['add_time']
    column_default_sort = ('add_time', True)



# Flask views
@app.route('/')
def index():
    # return render_template('index.html')
    return redirect('/admin')

@app.route("/statistic", methods=["GET"])
def statistic():

    statistic_result = {}
    lines = codecs.open(PROJECT_ROOT + '/web/cate_data.txt','r',encoding='utf8').readlines()
    first_cate_list = [item.split(':')[0].strip() for item in lines]
    for first_cate in first_cate_list:
        number = MediaLabelData.objects.filter(first_cate=first_cate).count()
        statistic_result[first_cate] = number

    return jsonify({
        'name':statistic_result.keys(),
        'data':statistic_result.values()
    })

# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, '爬虫数据可视化', index_view=MyAdminIndexView(), base_template='my_master.html')

# Add view
admin.add_view(MediaLabelDataView(MediaLabelData,name=u'媒体标签库'))
admin.add_view(MediaLabelDataStatisticsView(MediaLabelDataStatistics,name=u'媒体类别爬取统计'))

if __name__ == '__main__':

    app.run(debug=True, port=8080, host='0.0.0.0')
