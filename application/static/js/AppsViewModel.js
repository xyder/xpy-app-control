/***
 * Defines the apps view model module
 */
define([ 'jquery', 'knockout', 'komapping', 'AddEditViewModel' ], function($, ko, komapping, AddEditViewModel){
    // set the knockout mapper
    ko.mapper = komapping;

    return function (AppController) {
        var self = this;
        self.initial_load_done = false;
        self.controller = AppController;
        self.addVM = new AddEditViewModel(AppController);
        self.expanded = [];

        /***
         * checks if an item is part of the items array
         */
        var is_item = function(item){
            //noinspection JSValidateTypes
            return $.inArray(item, self.items()) != -1;
        };

        /***
         * sets the application controller attribute
         * @param controller
         */
        self.setController = function(controller){
            self.controller = controller;
            self.addVM.controller = controller;
        };

        /***
         * sets the page elements to expand and show the process list
         */
        self.toggle_proc_list = function(i, val){
            var list = $('#proc_list_' + i);
            var caret = $('#item_' + i + ' td.success span.caret_parent');
            // if val is undefined, use the current visibility as value
            val = (val == undefined) ? !list.is(':visible') : val;
            list.toggle(val);
            caret
                .toggleClass('dropup', val)
                .toggleClass('dropdown', val);
            return val;
        };

        /***
         * triggers and add or an edit operation
         */
        self.add_edit = function() {
            if(!self.controller.server_params.is_authenticated){
                self.controller.prompt_login(true);
                return;
            }
            // checking if 'this' is called from the parent
            if(this == self){
                self.addVM.fetch_item();
            } else {
                // checking if this is called from an element from self.items
                if(is_item(this)){
                    // noinspection JSUnresolvedFunction
                    self.addVM.fetch_item(this.app_item().url());
                } else {
                    console.error('The calling object is not the root or an item of this array.');
                }
            }
        };

        /***
         * requests the deletion of an item.
         */
        self.remove = function () {
            if(is_item(this)){
                if(!self.controller.server_params.is_authenticated) {
                    self.controller.prompt_login(true);
                    return;
                }

                var url = this.app_item().url();
                // delete any previously installed events
                self.controller.ask_question('Are you sure you want to delete this item?', function(){
                    // noinspection JSUnresolvedFunction
                    self.controller.ajax(url, 'DELETE').done(self.update);
                });
            } else {
                console.error('The calling object is not an item of this array.');
            }
        };

        /***
         * sends a request to run the command corresponding to an application item
         */
        self.run = function () {
            // check if this is an item from the items array
            if(is_item(this)){
                // build and send the request
                // noinspection JSUnresolvedFunction
                self.controller.run_rpc_method(self.controller.RPC_START_CMD, {'app_id': this.app_item().id()});
            } else {
                console.error('The calling object is not an item of this array.');
            }
        };

        /***
         * sends a request to stop a process
         */
        self.stop_process = function () {
            // check if this item is from the items array
            if(is_item(this)){
                // 'this' is an item entry. will stop all associated processes
                // noinspection JSUnresolvedFunction
                self.controller.run_rpc_method(self.controller.RPC_STOP_CMD, {'app_id': this.app_item().id()});
            } else {
                // double check if 'this' is a process entry. will stop this process only
                // noinspection JSUnresolvedFunction
                var pid = this.ProcessId();
                if(pid){
                    self.controller.run_rpc_method(self.controller.RPC_STOP_PROCESS, {'pid': pid});
                }
            }
        };

        /***
         * Sets the expanded flag for this item
         */
        self.expand_proc_list = function() {
            var i = self.items.indexOf(this);
            //noinspection JSUnresolvedFunction
            if(this.proc_no() != 0) {
                self.expanded[i] = self.toggle_proc_list(i);
            }
        };
    };
});