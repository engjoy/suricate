# coding=utf-8

'''
Main WSGI based app.

Assumes that there is an 'UID' key in the environ. Please make sure that the
WSGI middleware adds this.
'''

__author__ = 'tmetsch'

import bottle
import os

from StringIO import StringIO

import analytics.notebooks
import data.object_store


class AnalyticsApp(object):
    '''
    Analytics Web Application. WSGI app can be retrieved by calling
    'get_wsgi_app'.
    '''

    def __init__(self, host, port):
        '''
        Initialize the Web Application

        :param host: Hostname of a MongoDB server.
        :param port: Port of a MongoDB server.
        '''
        self.app = bottle.Bottle()
        # TODO: look into supporting other store types.
        self.obj_str = data.object_store.MongoStore(host, port)
        self.ntb_str = analytics.notebooks.NotebookStore(host, port)
        self._setup_routing()

    def _setup_routing(self):
        '''
        Setup the routing.
        '''
        self.app.route('/', ['GET'], self.index)
        self.app.route('/static/<filepath:path>', ['GET'], self.static)
        # # data
        self.app.route('/data', ['GET'],
                       self.list_data_sources)
        self.app.route('/data/<iden>', ['GET'],
                       self.retrieve_data_source)
        self.app.route('/data/upload', ['POST'],
                       self.create_data_source)
        self.app.route('/data/delete/<iden>', ['POST'],
                       self.delete_data_source)
        # analysis
        self.app.route('/analysis', ['GET'],
                       self.list_notebooks)
        self.app.route('/analysis/<iden>', ['GET'],
                       self.retrieve_notebook)
        self.app.route('/analysis/<iden>/add/<old_id>', ['POST'],
                       self.add_item_to_notebook)
        self.app.route('/analysis/<iden>/edit/<line_id>', ['GET'],
                       self.edit_item_in_notebook)
        self.app.route('/analysis/<iden>/remove/<line_id>', ['POST'],
                       self.remove_item_from_notebook)
        self.app.route('/analysis/upload', ['POST'],
                       self.create_notebook)
        self.app.route('/analysis/download/<iden>', ['GET'],
                       self.download_notebook)
        self.app.route('/analysis/delete/<iden>', ['POST'],
                       self.delete_notebook)
        # processing
        self.app.route('/process', ['GET'],
                       self.list_processings)

    def get_wsgi_app(self):
        '''
        Return the WSGI app.
        '''
        return self.app

    # Generic part

    @bottle.view('index.tmpl')
    def index(self):
        '''
        Initial view.
        '''
        uid = bottle.request.get_header('X-Uid')
        return {'uid': uid}

    def static(self, filepath):
        '''
        Serve static files.
        :param filepath:
        '''
        return bottle.static_file('web/static/' + filepath, root='..')

    # Data

    @bottle.view('data_srcs.tmpl')
    def list_data_sources(self):
        '''
        List all data sources.
        '''
        uid = bottle.request.get_header('X-Uid')
        tmp = self.obj_str.list_objects(uid)
        return {'data_objs': tmp, 'streams': None, 'uid': uid}

    def create_data_source(self):
        '''
        Create a new data source.
        '''
        uid = bottle.request.get_header('X-Uid')
        upload = bottle.request.files.get('upload')
        name, ext = os.path.splitext(upload.filename)
        if ext not in '.json':
            return 'File extension not supported.'

        self.obj_str.create_object(uid, upload.file.getvalue())
        bottle.redirect('/data')

    @bottle.view('data_src.tmpl')
    def retrieve_data_source(self, iden):
        '''
        Retrieve single data source.

        :param iden: Data source identifier.
        '''
        uid = bottle.request.get_header('X-Uid')
        tmp = self.obj_str.retrieve_object(uid, iden)
        return {'iden': iden, 'content': tmp, 'uid': uid}

    def delete_data_source(self, iden):
        '''
        Delete data source.

        :param iden: Data source identifier.
        '''
        uid = bottle.request.get_header('X-Uid')
        self.obj_str.delete_object(uid, iden)
        bottle.redirect('/data')

    # Analysis part

    @bottle.view('notebooks.tmpl')
    def list_notebooks(self):
        '''
        Lists all notebooks.
        '''
        uid = bottle.request.get_header('X-Uid')
        tmp = self.ntb_str.list_notebooks(uid)
        return {'notebooks': tmp, 'uid': uid}

    def create_notebook(self):
        '''
        Create a new notebook.

        When code is uploaded add it to the notebook.
        '''
        uid = bottle.request.get_header('X-Uid')
        iden = bottle.request.forms.get('iden')
        upload = bottle.request.files.get('upload')
        code = []
        if upload is not None:
            name, ext = os.path.splitext(upload.filename)
            if ext not in '.py':
                return 'File extension not supported.'

            code = upload.file.getvalue().split('\n')

        self.ntb_str.get_notebook(uid, iden, init_code=code)
        bottle.redirect('/analysis')

    @bottle.view('notebook.tmpl')
    def retrieve_notebook(self, iden):
        '''
        Enables interactions with one notebook.

        :param iden: Notebook identifier.
        '''
        uid = bottle.request.get_header('X-Uid')
        ntb = self.ntb_str.get_notebook(uid, iden)
        res = ntb.get_results()
        return {'iden': iden, 'uid': uid, 'output': res,
                'default': ntb.white_space}

    def delete_notebook(self, iden):
        '''
        Delete a notebook.

        :param iden: Notebook identifier.
        '''
        uid = bottle.request.get_header('X-Uid')
        self.ntb_str.delete_notebook(uid, iden)
        bottle.redirect('/analysis')

    def add_item_to_notebook(self, iden, old_id):
        '''
        Add a item to a notebook.

        :param old_id: Identifier of last line.
        :param iden: Notebook identifier.
        '''
        cmd = bottle.request.forms['cmd']
        uid = bottle.request.get_header('X-Uid')
        ntb = self.ntb_str.get_notebook(uid, iden)
        if cmd == '':
            ntb.update_line(old_id, '\n', replace=False)
        elif len(ntb.white_space) != 0:
            ntb.update_line(old_id, '\n' + cmd, replace=False)
        else:
            ntb.add_line(cmd)
        bottle.redirect('/analysis/' + iden)

    @bottle.view('edit_code.tmpl')
    def edit_item_in_notebook(self, iden, line_id):
        '''
        Edit an item in a notebook.

        :param line_id: Identifier of the loc.
        :param iden: Notebook identifier.
        '''
        uid = bottle.request.get_header('X-Uid')
        ntb = self.ntb_str.get_notebook(uid, iden)
        if bottle.request.GET.get('save', '').strip():
            line = bottle.request.GET.get('cmd', '').strip()
            ntb.update_line(line_id, line)
            bottle.redirect("/analysis/" + iden)
        else:
            code = ntb.src[line_id]
            return {'uid': uid, 'url': iden, 'old': code, 'line_id': line_id}

    def remove_item_from_notebook(self, iden, line_id):
        '''
        Remove an item from a notebook.

        :param line_id: Identifier of the loc.
        :param iden: Notebook identifier.
        '''
        uid = bottle.request.get_header('X-Uid')
        ntb = self.ntb_str.get_notebook(uid, iden)
        ntb.remove_line(line_id)
        bottle.redirect('/analysis/' + iden)

    def download_notebook(self, iden):
        '''
        Download a notebook.

        :param iden: Notebook identifier.
        '''
        uid = bottle.request.get_header('X-Uid')
        tmp = self.ntb_str.get_notebook(uid, iden)
        tmp_file = StringIO()
        for item in analytics.notebooks.PRELOAD.split('\n'):
            tmp_file.write(item + '\n')
        for item in tmp.get_lines():
            line = item + '\n'
            line = line.replace('\t', '')
            if line[0] != ' ':
                line += '\n'
            tmp_file.write(line)
        # will force browsers to download...
        bottle.response.set_header('Content-Type', 'ext/x-script.python')
        bottle.response.set_header('content-disposition',
                                   'inline; filename=notebook.py')
        return tmp_file.getvalue()

    # Processing

    @bottle.view('processing.tmpl')
    def list_processings(self):
        '''
        Processing part.
        '''
        uid = bottle.request.get_header('X-Uid')
        return {'uid': uid}
