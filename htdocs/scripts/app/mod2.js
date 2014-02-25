define([
    'dojo/_base/declare'
], function (declare) {
    return declare(null, {

        constructor: function () {
            this.test = "test 2 data";
        },
        get: function () {
            return this.test;
        }

    });//declare
});//define
