/***
 * defines a server view model module
 */
define(function(){
    return function (AppController) {
        var self = this;
        self.controller = AppController;

        /***
         * flag that determines if periodic refreshing is triggered
         */
        self.toggle_refresh = function() {
            self.controller.is_refreshing = !self.controller.is_refreshing;
            $('#refresh_switch').toggleClass('btn-default-toggle', self.controller.is_refreshing);
        };

        /***
         * send a request to shut down the server
         */
        self.shutdown = function () {
            self.controller.ajax(self.controller.BASE_API_SERVER_CMD, 'POST', {command: 'SHUTDOWN'});
        };

        /***
         * triggers the login process
         */
        self.login = function () {
            if (self.controller.is_logged_in) {
                self.controller.username = '';
                self.controller.password = '';
                self.controller.set_login_status(false);
            } else {
                $('#login').modal('show');
            }
        };
    };
});