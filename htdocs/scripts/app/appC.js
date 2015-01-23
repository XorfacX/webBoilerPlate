/**@license
 * Copyright (c) 2013-2015, XorfacX - FairyDwarves
 * Please report to LICENSE.md file.
 */

/**
* Main file
*/
"use strict"; //enable strict mode


define([
    'dojo/_base/lang',
    'dojo/_base/declare',
    "dojo/on",
    "dojo/ready",
    "dojo/Deferred",
    "app/system",
    "app/appM",
    "app/appV",
    "app/sound",
    "app/Environment"
], function (lang, declare, on, ready, Deferred, system, model, view, appSound) {

    /** @private */
    var context, screenTO = 2000; //screenTO == sum of transition duration defined inside css for #title and #logo

    /**
     * Create the whole app view
     * This is the controller part
     */
    return declare(null, {
        /**
         * @constructor
         */
        constructor: function () {
            context = this; //need to keep track inside "on" and "require" calls if we don't want to (or can't) use lang.hitch

            var forcedNode = (location.search.match(/n=(\S+)/) ? RegExp.$1 : undefined); //"n", node parameter

            //set AppEnv
            setEnvironment();
            system.LSKey = AppEnv.LSKey;

            //create the gloabal app Deferred
            window.appDeferred = new Deferred();

            //init sound
            //appSound.init(system.LSKey);

            //create the model
            this.model = new model();

            //create the default view empty (can't be populated until appDeferred is resolved)
            var aV = this.view = new view();

            //wait for dom ready
            ready(function () {
                if (typeof forcedNode == "undefined") {
                    aV.showTitle("My App Title".replace(/_/gi, " ").replace(/ /g, "<br/>")); //replace potential underscore with space than spaces with <br/> tag

                    var onSig = on.once(aV.getRawView(), "click", function (e) {
                        context._Title2Logo(aV, to);
                    });

                    var to = setTimeout(function () {
                        context._Title2Logo(aV, onSig); //TODO: fix, CANT use on.emit
                    }, screenTO);
                } else { //to display directly a specific node
                    this._launch(aV, forcedNode);
                }
            }); //ready
        }, //constructor

        model: undefined,
        view: undefined,

        /**
         * Transition from Title to Logo screen
         *
         * @private
         */
        _Title2Logo: function (aV, _signal) {
            if (_signal) {
                if (typeof _signal.remove == "function") { //remove event if called through setTimeout
                    _signal.remove();
                } else {
                    clearTimeout(_signal); //cleartimeout if called through on event
                }
            }

            aV.hideTitle().showLogo();

            var onSig = on.once(aV.getRawView(), "click", function (e) {
                context._Logo2Launch(aV, to);
            });

            var to = setTimeout(function () {
                context._Logo2Launch(aV, onSig);
            }, screenTO);
        },

        /**
         * Transition from Logo to Launch screen
         *
         * @private
         */
        _Logo2Launch: function (aV, _signal) {
            if (_signal) {
                if (typeof _signal.remove == "function") { //remove event if called through setTimeout
                    _signal.remove();
                } else {
                    clearTimeout(_signal); //cleartimeout if called through on event
                }
            }

            context._launch(aV);
        },

        /**
         * Launch the view
         * @private
         */
        _launch: function (aV, node) {
            window.appDeferred.then( //waiting for whatever we want to preload
                function (deferredRes) { //when wating is over call this function
                    console.log(deferredRes);
                    aV.hideLogo();
                    context.reset();
                });
            window.appDeferred.resolve("Loading successful"); //TOSET: proper location of this code when all you wan to preload is done
        },

        /**
         * Reset the displayed view
         *
         * @param nId {string}, node id to display
         * 
         * @return {!object} this, for chaining
         */
        reset: function (nId) {
            //TOSET: APP CODE GOES HERE

            this.view.reset();
            on(document, "touched, click", lang.hitch(this, function (event) {
                var res = "App model says: " + this.model.get();
                console.log(res);
                this.view.display(res);
            }));
        }
    });  //declare
});     //define

