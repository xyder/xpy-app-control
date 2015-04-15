/***
 * Main application controller module.
 */
define([ 'jquery', 'knockout', 'komapping', 'AppsViewModel' ], function ($, ko, komapping, AppsViewModel){
    // set the knockout mapper
    ko.mapper = komapping;
    return function(){
        var self = this;
        // set the server url constants
        self.BASE_API = '/api/v1.0/';
        self.BASE_API_APPS = self.BASE_API + 'apps';
        self.BASE_API_APPS_LIST = self.BASE_API_APPS + '/list';
        self.BASE_API_APPS_ADD = self.BASE_API_APPS + '/add';
    
        self.username = '';
        self.password = '';
        // flag that specifies if the user is logged in
        self.is_logged_in = false;
        // flag that specifies if the client will perform a refresh
        self.is_refreshing = true;
        self.appsViewModel = new AppsViewModel(self);

        // RPC constants:
        self.RPC_URL = '/rpc';
        self.RPC_BASE = 'RPCServer.';
        self.RPC_SHUTDOWN = self.RPC_BASE + 'shutdown';
        self.RPC_START_CMD = self.RPC_BASE + 'start_command';
        self.RPC_STOP_CMD = self.RPC_BASE + 'stop_command';
        self.RPC_STOP_PROCESS = self.RPC_BASE + 'stop_process';
        self.RPC_CHECK_AUTH = self.RPC_BASE + 'check_auth';

        /***
         * Sets the server status html accordingly
         *
         * @param val boolean determining if the server is online or offline
         */
        self.set_server_status = function(val){
            $('#pingpong-server')
                .html(val ? 'Online': 'Offline')
                .toggleClass('label-default', !val)
                .toggleClass('label-success', val)
                .css('color', val ? 'black' : 'inherit');
        };

        /***
         * refreshes the app list and timestamp and all relevant page elements
         */
        self.auto_refresh = function () {
            if(self.is_refreshing) {
                var d = new Date();
                // build and set the timestamp string
                var str = d.toDateString() + " -- " + d.toTimeString().substr(0, d.toTimeString().lastIndexOf(" ("));
                $('#ticker_x').toggle();
                $('#ticker_p').toggle();
                $("#pingpong-text").html(str);

                // refresh the app list
                self.ajax(self.BASE_API_APPS_LIST, 'GET').done(function (data) {
                    // fetch data and fill array
                    if(self.appsViewModel.initial_load_done){
                        // update the view model
                        ko.mapper.fromJS(data, {}, self.appsViewModel);
                    } else {
                        // initialize the view model
                        var mapping = {
                            $type: AppsViewModel
                        };
                        self.appsViewModel = ko.mapper.fromJS(data, mapping);
                        self.appsViewModel.setController(self);
                        ko.applyBindings(self.appsViewModel, $('#apps_container')[0]);
                        self.appsViewModel.initial_load_done = true;
                    }

                    // iterate over previously expanded items
                    for(var elem in self.appsViewModel.expanded){
                        // check if item still has running processes and ignore (collapse) if not
                        //noinspection JSUnresolvedFunction,JSValidateTypes
                        if(self.appsViewModel.items()[elem].proc_no() !=0) {
                            // set and toggle the expanded state of the item
                            //noinspection JSValidateTypes,JSUnresolvedFunction
                            var is_expanded = self.appsViewModel.items()[elem].proc_no() != 0
                                && self.appsViewModel.expanded[elem];
                            self.appsViewModel.toggle_proc_list(elem, is_expanded);
                        }
                    }

                    //show title for extra-long lines
                    $('#apps_table').find('div.long_cell').each(function(){
                        var item = $(this);
                        item.prop('title', item.html());
                    });
                });
            }
        };

        /***
         * Fills the correesponding page elements with information regarding login state.
         * @param val boolean that determines if logged on or off.
         */
        self.set_login_status = function (val) {
            if (val) {
                $('#pingpong-user').html('Logged in as <span id="pingpong-username">' + self.username + '</span>');
                $('#login_button').html('Logout');
                self.is_logged_in = true;
            } else {
                $('#pingpong-user').html('Not Logged In');
                $('#login_button').html('Login');
                self.is_logged_in = false;
            }
        };

        /***
         * Performs an ajax call to the specified uri with the given method and data
         * @param uri path to be used in the ajax call
         * @param method http method to be used
         * @param data object to be converted to json and sent attached to the request
         * @returns the return value from the jquery ajax call
         */
        self.ajax = function (uri, method, data) {
            return $.ajax({
                url: uri,
                type: method,
                contentType: 'application/json',
                accepts: 'application/json',
                cache: false,
                dataType: 'json',
                data: JSON.stringify(data),
                headers: {
                    'Authorization': 'Basic ' + btoa(self.username + ':' + self.password)
                },
                timeout: 1000,
                statusCode: {
                    // success
                    200: function () {
                        self.set_server_status(true)
                    },
                    // unauthorized
                    403: function(jqXHR){
                        if (jqXHR.status == 403) {
                            self.set_login_status(false);
                            $('#login').modal('show');
                        } else {
                            console.log('Ajax error code: ' + jqXHR.status);
                        }
                    },
                    // no response
                    0: function () {
                        self.set_server_status(false)
                    }
                }
            });
        };

        self.run_rpc_method = function(method, params){
            var req_object = {
                'id': Math.floor(Math.random()*1001),
                'method': method
            };
            if( params != undefined ){
                req_object.params = params;
            }
            return self.ajax(self.RPC_URL, 'POST', req_object);
        };

        /***
         * Sets login information and requests server to validate the authentication
         */
        self.login = function (username, password) {
            self.username = username;
            self.password = password;
            self.run_rpc_method(self.RPC_CHECK_AUTH).done(function(){
                self.set_login_status(true);
            });
        };
    };
});