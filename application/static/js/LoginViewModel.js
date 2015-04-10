/***
 * defines a login view model module
 */
define([ 'knockout' ], function (ko) {
    return function (AppController) {
        var self = this;
        self.controller = AppController;
        self.username = ko.observable();
        self.password = ko.observable();

        /***
         * triggers the login process
         */
        self.login = function () {
            $('#login').modal('hide');
            self.controller.login(self.username(), self.password());
            self.username("");
            self.password("");
        };

        /***
         * listens for the key press event and triggers the login process if Return is pressed
         */
        self.key_event = function (data, event) {
            if (event.which == 13) {
                self.login(self.username(), self.password());
                // consume the event
                return false;
            }
            //if Return was not pressed, don't consume the event
            return true;
        }
    }
});