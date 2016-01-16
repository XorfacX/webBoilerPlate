/**
 * Copyright (c) 2013-2016, XorfacX - FairyDwarves
 * Please report to LICENSE.md file.
 */

define([
    'dojo/_base/declare',
    "dojo/dom-construct",
    "dojo/dom-class",
    "dojo/dom-style",
    "dojox/mobile/ScrollableView"
    //https://dojotoolkit.org/reference-guide/1.10/dojox/mobile.html
], function (declare, domConstruct, domClass, domStyle, ScrollableView) {

    /**
    * Create the whole app view
    * This is the view part
    */
    return declare(null, {
        /**
        * @constructor
        */
        constructor: function () {
            appView = new ScrollableView(null, "view");  //"view", same id as in index.html
        },

        /**
         * Accessor to the dojox mobile raw view
         *
         * @return {object} the dojox.mobile.view
         */
        getRawView: function () {
            return appView;
        },

        /**
        * So the view with Title
        *
        * @param title {string}, the title to show as it
        * 
        * @return {object} this, for chaining
        */
        showTitle: function (title) {
            domConstruct.create("div", { id: "title", innerHTML: title }, appView.containerNode);
            setTimeout(function () {
                domStyle.set("title", { opacity: "0.01" });
            }, 10);
            appView.startup();
            return this;
        },
        /**
        * Clean the view from Title
        *
        * @return {object} this, for chaining
        */
        hideTitle: function () {
            domConstruct.destroy("title");
            return this;
        },

        /**
        * Show the view with FD Logo
        *
        * @return {object} this, for chaining
        */
        showLogo: function () {
            domConstruct.create("div", { id: "logo" }, appView.containerNode);
            setTimeout(function () {
                domStyle.set("logo", { opacity: "0.01" });
            }, 10);
            appView.startup();
            return this;
        },
        /**
        * Clean the view from FD Logo
        *
        * @return {object} this, for chaining
        */
        hideLogo: function () {
            domConstruct.destroy("logo");
            return this;
        },

        /**
         * reset display
         */
        reset: function () {
            domConstruct.create("h1", { innerHTML: "Press Me!!", style: "color:white;" }, appView.containerNode);
        },

        /**
         * Display a message in an alert
         * 
         * @param msg {*}, the message to display
         */
        display: function (msg) {
            alert(JSON.stringify(msg));
        }

    });  //declare
});     //define
