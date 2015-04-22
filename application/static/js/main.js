// set to '' before deploy to reduce load time
var timestamp = '' + '.js?ts=' + (new Date()).getTime();

// add this parameter with version number when in production,
// or timestamp to force reload all scripts each time
// urlArgs: "ts=" + (new Date()).getTime()
require.config({
    waitSeconds: 200,
    paths: {
        jquery: '../libs/jquery-2.1.3',
        knockout: '../libs/knockout-3.2.0',
        komapping: '../libs/knockout.mapper',
        bootstrap: '../libs/bootstrap-3.3.2-dist/js/bootstrap',
        controller: 'AppController' + timestamp,
        AddEditViewModel: 'AddEditViewModel' + timestamp,
        AppsViewModel: 'AppsViewModel' + timestamp
    },
    shim: {
        komapping: {
            deps: ['knockout'],
            exports: 'komapping'
        },
        bootstrap: {
            deps: ['jquery']
        }
    }
});

/***
 * main application function
 */
require([   'jquery', 'knockout', 'komapping', 'controller', 'AppsViewModel', 'bootstrap'],
    function($, ko, komapping, AppController){
        var XPyAC = new AppController();

        // execute when document is loaded
        $(document).ready(function () {
            // fetch server params from page
            XPyAC.server_params = window.server_params;

            // set up a 1024 number multiple formatter to round RAM values
            ko.extenders.numeric = function(target){
                var suff = "K";
                var n = target();
                //when larger than 100 000, round to mega
                if(n > 100000){
                    suff = "M";
                    n = Math.round(n / 1024);
                }
                return n.toString().replace(/\B(?=(?:\d{3})+(?!\d))/g, " ") + " " + suff;
            };

            // set up the login dialog
            var login_dialog = $('#login');
            login_dialog.on('shown.bs.modal', function () {
                $('#input_username').focus();
            });

            // wire button events
            $('#login_button').click(function(){
               login_dialog.modal('show');
            });

            $('#refresh_switch').click(XPyAC.toggle_refresh);

            // show login dialog if server sent a retry flag
            if(XPyAC.server_params.retry_login){
                login_dialog.modal('show');
            }

            // set up the periodic refresh function
            XPyAC.auto_refresh();
            setInterval(XPyAC.auto_refresh, 2500);
        });
});