import subprocess
import application


# prepend '_' to function name to make it uncallable
from application.libs.helper_functions import terminate_process


def create_message(code, message, arg=''):
    return {'code': code, 'message': message % arg if '%s' in message else message}


class RPCServer:
    """
    Class that provides a set of RPCs
    """

    SUCCESS_MSG = create_message(200, 'SUCCESS')
    APP_NOT_FOUND_MSG = create_message(404, 'Application item not found.')
    INVALID_PID_STR = 'PID number %s is invalid or process not found.'
    WIN_ERROR_STR = 'WindowsError %s received.'
    FILE_NOT_FOUND_STR = 'File "%s" not found.'

    @staticmethod
    def shutdown():
        """
        Sends a signal for the thread to terminate.
        """
        print("We're going down..")
        application.app.thread.exit_signal.emit()
        return RPCServer.SUCCESS_MSG

    @staticmethod
    def start_command(app_id):
        """
        Executes the command associated with the specified application item.

        :param app_id: The application item id.
        """
        # fetch the application item
        app_item = application.models.AppItem.query.get(app_id)
        if app_item is None:
            return RPCServer.APP_NOT_FOUND_MSG

        if app_item.start_file:
            try:
                subprocess.Popen(app_item.get_start_command(), shell=app_item.start_in_command_prompt)
            except FileNotFoundError:
                return create_message(404, RPCServer.FILE_NOT_FOUND_STR, app_item.get_start_command())
        return RPCServer.SUCCESS_MSG

    @staticmethod
    def stop_command(app_id):
        """
        Executes the command associated with stopping the specified application item.

        :param app_id: The application item id.
        """

        # if command not specified, pull list of processes and send sigterm to each
        # fetch the application item
        app_item = application.models.AppItem.query.get(app_id)
        if app_item is None:
            return RPCServer.APP_NOT_FOUND_MSG

        if app_item.stop_file:
            # use command to stop app
            try:
                subprocess.Popen(app_item.get_stop_command(), shell=app_item.stop_in_command_prompt)
            except FileNotFoundError:
                return create_message(404, RPCServer.FILE_NOT_FOUND_STR, app_item.get_stop_command())
            return RPCServer.SUCCESS_MSG
        else:
            # pull list of processes and send sigterm to each
            from application.resources.app_list_resource import AppListResource
            pids = AppListResource.parse_process_list_for_app(app_item)
            for pid in pids:
                try:
                    terminate_process(int(pid, 10))
                except ValueError:
                    pass
                except WindowsError as e:
                    if e.winerror != 87:
                        return create_message(405, RPCServer.WIN_ERROR_STR, e.winerror)
            return RPCServer.SUCCESS_MSG

    @staticmethod
    def stop_process(pid):
        """
        Terminates a process with the specified pid.

        :param pid: the process id that is to be terminated.
        """
        # send sigterm to specified process
        try:
            if isinstance(pid, int):
                terminate_process(pid)
            else:
                terminate_process(int(pid, 10))
        except ValueError:
            return create_message(405, RPCServer.INVALID_PID_STR, pid)
        except WindowsError as e:
            if e.winerror != 87:
                return create_message(405, RPCServer.WIN_ERROR_STR, e.winerror)
            else:
                return create_message(405, RPCServer.INVALID_PID_STR, pid)
        return RPCServer.SUCCESS_MSG

    @staticmethod
    def check_auth():
        """
        Used as a means to check authentication. Always returns SUCCESS.
        """
        return RPCServer.SUCCESS_MSG
