/**
 * Copyright (c) 2013-2015, XorfacX - FairyDwarves
 * Please report to LICENSE.md file.
 */

define(['dojo/_base/declare', "app/system"], function (declare, system) {

    /**
    * Create the whole app view
    * This is the model part
    */
    return declare(null, {
        /**
        * @constructor
        */
        constructor: function () {
            this._loadingStatus = "OK";
        },
        _loadingStatus: undefined,

        /**
         * Return _loadingStatus
         * 
         * @return _loadingStatus object
         */
        get: function () {
            return this._loadingStatus;
        }

    });  //declare
});     //define
