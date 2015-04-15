/***
 * Module which defines a view model for the Add dialog.
 */
define([ 'jquery', 'knockout', 'komapping' ], function($, ko, komapping){
    ko.mapper = komapping;
    return function(AppController) {
        var self = this;
        self.controller = AppController;
        // flag that determines if the item object is bound to the dialog
        self.is_bound = false;
        self.item = ko.observable();
        self.item_id = undefined;
        self.dialog = $('#add');

        /***
         * Sends an add or edit request to the server and updates on return.
         */
        self.commit = function(){
            // check if the item id was fetched previously to determine the type of operation
            if(self.item_id != undefined){
                // send an edit request to the server with the item data and update on return
                self.controller.ajax(self.controller.BASE_API_APPS + '/' + self.item_id, 'PUT', ko.mapper.toJS(self.item))
                    .done(self.controller.appsViewModel.update);
            } else {
                // send an add request to the server with the itme data and update on return
                self.controller.ajax(self.controller.BASE_API_APPS_ADD, 'POST', ko.mapper.toJS(self.item))
                    .done(self.controller.appsViewModel.update);
            }
            // hide the add/edit dialog
            self.dialog.modal('hide');
        };

        /***
         * Fills and shows the dialog with the specified data.
         *
         * @param data the specified data.
         */
        var fill_and_show = function(data) {
            // fill the item object with the data
            ko.mapper.fromJS(data, {}, self.item);

            // set the callback to request a change to the server
            self.item().callback = self.commit;

            // bind the item if it was not previously bound to the dialog
            if (!self.is_bound) {
                ko.applyBindings(self.item, self.dialog[0]);
                self.is_bound = true;
            }

            // show the dialog
            self.dialog.modal('show');
        };

        /***
         * Retrieves the item data from the server and shows the corresponding dialog
         *
         * @param [item_id] the item id used to specify which object to fetch
         */
        self.fetch_item = function(item_id){
            // set the view model item id
            self.item_id = item_id;
            // check if item id was given to determine the type of operation
            if(self.item_id != undefined){
                // fetch the item with the specified id from the server
                $('#add_dialog_label').html('Edit Application');
                self.controller.ajax(self.controller.BASE_API_APPS + '/' + item_id).done(fill_and_show);
            } else {
                // fetch a default item from the server and use it to build the add form
                $('#add_dialog_label').html('Add Application');
                self.controller.ajax(self.controller.BASE_API_APPS).done(fill_and_show);
            }
        }
    };
});