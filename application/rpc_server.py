import subprocess
import application


# prepend '_' to function name to make it uncallable
from application.libs.helper_functions import terminate_process


class RPCServer:
    """
    Class that provides a set of RPCs
    """

    SUCCESS = 'SUCCESS'

    @staticmethod
    def test():
        return 'test was successful.'

    @staticmethod
    def shutdown():
        """
        Sends a signal for the thread to terminate.
        """
        print("We're going down..")
        application.app.thread.exit_signal.emit()
        return RPCServer.SUCCESS

    @staticmethod
    def start_command(app_id):
        """
        Executes the command associated with the specified application item.

        :param app_id: The application item id.
        """
        # fetch the application item
        app_item = application.models.AppItem.query.get_or_404(app_id)
        if app_item.start_file:
            try:
                subprocess.Popen(app_item.get_start_command(), shell=app_item.start_in_command_prompt)
            except FileNotFoundError:
                raise Exception('404: File "' + app_item.get_start_command() + '" not found.')
        return RPCServer.SUCCESS

    @staticmethod
    def stop_command(app_id):
        """
        Executes the command associated with stopping the specified application item.

        :param app_id: The application item id.
        """

        # if command not specified, pull list of processes and send sigterm to each
        # fetch the application item
        app_item = application.models.AppItem.query.get(app_id)
        if app_item is not None:
            if app_item.stop_file:
                # use command to stop app
                try:
                    subprocess.Popen(app_item.get_stop_command(), shell=app_item.stop_in_command_prompt)
                except FileNotFoundError:
                    raise Exception('404: File "' + app_item.get_stop_command() + '" not found.')
                return RPCServer.SUCCESS
            else:
                # pull list of processes and send sigterm to each
                pids = application.AppListResource.parse_process_list_for_app(app_item)
                for pid in pids:
                    try:
                        terminate_process(int(pid, 10))
                    except ValueError:
                        pass
                    except WindowsError as e:
                        if e.winerror != 87:
                            raise
                return RPCServer.SUCCESS
        else:
            raise Exception('404: Application item not found.')

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
            raise Exception('405: PID is invalid.')
        except WindowsError as e:
            if e.winerror == 87:
                raise Exception('405: PID is invalid or process not found.')
            else:
                raise
        return RPCServer.SUCCESS

    @staticmethod
    def check_auth():
        """
        Used as a means to check authentication. Always returns SUCCESS.
        """
        return RPCServer.SUCCESS