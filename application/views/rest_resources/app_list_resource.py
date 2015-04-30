from flask.ext.restful import Resource, fields, marshal_with

import subprocess
import psutil

from application.utils.helper_functions import fields_str_from_keys, str_to_pair
from application import models
from . import app_fields_extended


class AppListResource(Resource):
    """
    Resource class that processes a GET request and returns the list of registered application items
    with the running processes that belong to each of them.
    """
    # fields of a process element
    processes_fields = {
        'ProcessId': fields.Integer,
        'Name': fields.String,
        'CommandLine': fields.String,
        'ExecutablePath': fields.String
    }

    # fields of an extended process element, which also contains details of matching running processes
    processes_fields_extended = processes_fields.copy()
    processes_fields_extended['ProcMem'] = fields.Integer
    app_list_fields = {
        'app_item': fields.Nested(app_fields_extended),
        'proc_no': fields.Integer,
        'proc_mem_total': fields.Integer,
        'proc_list': fields.Nested(processes_fields_extended)
    }

    # fields of a app list element
    app_list_fields = {
        'items': fields.Nested(app_list_fields)
    }

    @staticmethod
    def get_process_list():
        """
        Executes a wmic command with the running processes list.

        :return: array containing the command output split into non-empty lines
        """
        cmd = 'wmic process get '
        cmd += fields_str_from_keys(AppListResource.processes_fields) + ' /format:list'
        lines = subprocess.getoutput(cmd).splitlines()

        # remove empty lines
        lines = [s for s in lines if s]
        return lines

    @staticmethod
    def parse_process_list():
        """
        Fetches and processes a list of running processes.

        :return: A collection of items representing processes as dictionaries.
        """
        lines = AppListResource.get_process_list()
        items = []
        item = {}
        for line in lines:
            item.update(str_to_pair(line))
            # each process occupies 4 lines in the wmic output
            if len(item) == 4:
                items.append(item)
                item = {}
        return items

    @staticmethod
    def parse_process_list_for_app(app_item):
        """
        Fetches and processes a list of running processes belonging to a specific application item

        :param app_item: the application item of AppItem type

        :return: A coolection of items representing processes as dictionaries.
        """
        if app_item:
            lines = AppListResource.get_process_list()
            items = []
            item = {}
            for line in lines:
                item.update(str_to_pair(line))
                if len(item) == 4:
                    if app_item.compare_process(item):
                        items.append(item['ProcessId'])
                    item = {}
            return items
        else:
            return None

    @marshal_with(app_list_fields)
    def get(self):
        """
        Endpoint that responds to a GET request with a list of all registered application items,
        attaching a compilation of all running processes that belong to each of them.

        :return: A list of application items with attached information on corresponding running processes.
        """
        # fetch the process list
        proc_list = AppListResource.parse_process_list()
        items = []
        # fetch the appitem list from the database
        apps = models.AppItem.query.all()
        # initialize the return array
        for app_item in apps:
            items.append({
                'app_item': app_item,
                'proc_no': 0,
                'proc_mem_total': 0,
                'proc_list': []
            })
        # iterate over each process
        for proc in proc_list:
            # iterate over each 'empty' item
            for item in items:
                # check if the process matches the comparison method and term
                if item['app_item'].compare_process(proc):
                    # Store RAM usage in KB, per process and an application wide total.
                    try:
                        proc['ProcMem'] = psutil.Process(int(proc['ProcessId'])).get_memory_info()[0] / 1024
                    except psutil.NoSuchProcess:
                        proc['ProcMem'] = 0
                    item['proc_mem_total'] += proc['ProcMem']

                    # register process
                    item['proc_list'].append(proc)
                    item['proc_no'] += 1
        return {'items': items}
