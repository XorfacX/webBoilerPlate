define(['dojo/_base/declare'], function (declare) {

    return declare(null, {
        /**
        * Create The Shop Frame: description + secured payment iframe
        *
        * @constructor
        */
        constructor: function () {
            this.test = "test 1 data";
        },
        get: function () {
            return this.test;
        }

    }); //end declare
});     //define