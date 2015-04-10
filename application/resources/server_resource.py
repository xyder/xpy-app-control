from flask.ext.restful import Resource, reqparse, fields, marshal_with
import subprocess
from application import auth, app
from application.libs.helper_functions import terminate_process
from application.models import AppItem
from application.resources.app_list_resource import AppListResource


class ServerResource(Resource):
    """
    Resource class for server command processing.
    """
    # class wide decorator
    decorators = [auth.login_required]

    command_fields = {
        'Message': fields.String
    }
    SUCCESS = {'Message': 'SUCCESS'}

    def __init__(self):
        """
        Constructor. Builds the request parser and the command type dictionary
        :return:
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('command', type=str)
        self.reqparse.add_argument('args', type=str)
        self.commands = {
            'SHUTDOWN': self.shutdown_command,
            'CHECK_AUTH': self.generic_command,
            'START_APP': self.run_command,
            'STOP_APP': self.stop_command,
            'STOP_PROCESS': self.stop_process_command
        }

    @staticmethod
    def shutdown_command(args):
        """
        Sends a signal for the thread to terminate.

        :param args: necessary for command matching. ignored.
        """
        del args  # ignored
        print("We're going down..")
        app.thread.exit_signal.emit()
        return ServerResource.SUCCESS

    @staticmethod
    def generic_command(args):
        """
        Generic command type. Does nothing.

        :param args: necessary for command matching. ignored.
        """
        del args  # ignored
        return ServerResource.SUCCESS

    @staticmethod
    def run_command(args):
        """
        Executes the command associated with the specified application item.

        :param args: The application item id.
        """
        if args is not None:
            # fetch the application item
            app_item = AppItem.query.get_or_404(args)
            if app_item.start_file:
                try:
                    subprocess.Popen(app_item.get_start_command(), shell=app_item.start_in_command_prompt)
                except FileNotFoundError:
                    return {'Message': 'File "' + app_item.get_start_command() + '" not found.'}, 404
            return ServerResource.SUCCESS
        else:
            return {'Message': 'Command argument was not specified.'}, 405

    @staticmethod
    def stop_command(args):
        """
        Executes the command associated with stopping the specified application item.

        :param args: The application item id.
        """

        # if command not specified, pull list of processes and send sigterm to each
        if args is not None:
            # fetch the application item
            app_item = AppItem.query.get(args)
            if app_item is not None:
                if app_item.stop_file:
                    # use command to stop app
                    try:
                        subprocess.Popen(app_item.get_stop_command(), shell=app_item.stop_in_command_prompt)
                    except FileNotFoundError:
                        return {'Message': 'File "' + app_item.get_stop_command() + '" not found.'}, 404
                    return ServerResource.SUCCESS
                else:
                    # pull list of processes and send sigterm to each
                    pids = AppListResource.parse_process_list_for_app(app_item)
                    for pid in pids:
                        try:
                            terminate_process(int(pid, 10))
                        except ValueError:
                            pass
                        except WindowsError as e:
                            if e.winerror != 87:
                                raise
                    pass
            else:
                return {'Message': 'Application not found.'}, 404
        else:
            return {'Message': '"args" was not specified.'}, 405

    @staticmethod
    def stop_process_command(args):
        """
        Terminates a process with the specified pid.

        :param args: the process id that is to be terminated.
        """
        # send sigterm to specified process
        if args is not None:
            try:
                terminate_process(int(args, 10))
            except ValueError:
                return {'Message': '"args" field is invalid.'}, 405
            except WindowsError as e:
                if e.winerror == 87:
                    return {'Message': 'PID is invalid or process not found.'}, 405
                else:
                    raise
            return ServerResource.SUCCESS
        else:
            return {'Message': '"args" field was not specified.'}, 405

    @marshal_with(command_fields)
    def post(self):
        """
        Endpoint that receives and executes a server command.
        :return:
        """

        # get the request args
        args = self.reqparse.parse_args()
        if args['command']:
            if args['command'] in self.commands:
                # executed the specified command
                return self.commands[args['command']](args['args'])
            else:
                return {'Message': 'Command not found.'}, 404
        else:
            return {'Message': '"command" field was not specified.'}, 405