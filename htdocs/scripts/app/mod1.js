define([
    'dojo/_base/declare'
], function (declare) {
    return declare(null, {

        constructor: function () {
            this.test = "test 1 data";
        },
        get: function () {
            return this.test;
        }

    });//declare
});//define
