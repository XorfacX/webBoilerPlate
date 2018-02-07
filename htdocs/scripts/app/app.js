/**@license
 * Copyright (c) 2013-2018, XorfacX - FairyDwarves
 * Please report to LICENSE.md file.
 */

/**
* Main file
*/
//"use strict"; //enable strict mode


define([
    'dojo/_base/declare',
    'dojo/_base/lang',
    "dojo/on",
    "dojo/touch",
    "dojo/ready",
    "dojo/Deferred",
    "app/system",
    "app/appM",
    "app/appV",
    "app/Environment"
], function (declare, lang, on, touch, ready, Deferred, system, model, view) {

    /**
     * Create the whole app view
     * This is the controller part
     */
    return declare(null, {
        /**
         * @constructor
         */
        constructor: function () {

            var forcedNode = (location.search.match(/n=(\S+)/) ? RegExp.$1 : undefined); //"n", node parameter

            //set AppEnv
            setEnvironment();
            system.LSKey = AppEnv.LSKey;

            //create the gloabal app Deferred
            window.appDeferred = new Deferred();

            //create the model
            this.model = new model();

            //create the default view empty (can't be populated until appDeferred is resolved)
            var aV = this.view = new view();

            //wait for dom ready
            ready(lang.hitch(this, function () {
                if (typeof forcedNode == "undefined") {
                    aV.showTitle("My App Title".replace(/_/gi, " ").replace(/ /g, "<br/>")); //replace potential underscore with space than spaces with <br/> tag

                    var onSig = on.once(aV.getRawView(), "click", lang.hitch(this, function (e) {
                        this._Title2Logo(aV, to);
                    }));

                    var to = setTimeout(lang.hitch(this, function () {
                        this._Title2Logo(aV, onSig); //CANT use on.emit ...
                    }), this.screenTO);
                } else { //to display directly a specific node
                    this._launch(aV, forcedNode);
                }
            })); //ready
        }, //constructor

        model: undefined,
        view: undefined,

        screenTO: 2000, //screenTO == sum of transition duration defined inside css for #title and #logo

        /**
         * Transition from Title to Logo screen
         *
         * @private
         */
        _Title2Logo: function (aV, _signal) {
            if (_signal) {
                if (typeof _signal.remove == "function") { //remove event if called through dojo.on event
                    _signal.remove();
                } else {
                    clearTimeout(_signal); //clearTimeout if called through setTimeout
                }
            }

            aV.hideTitle().showLogo();

            var onSig = on.once(aV.getRawView(), "click", lang.hitch(this, function (e) {
                this._Logo2Launch(aV, to);
            }));

            var to = setTimeout(lang.hitch(this, function () {
                this._Logo2Launch(aV, onSig);
            }), this.screenTO);
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

            this._launch(aV);
        },

        /**
         * Launch the view
         * @private
         */
        _launch: function (aV, node) {
            window.appDeferred.then( //waiting for whatever we want to preload
                lang.hitch(this, function (deferredRes) { //when wating is over call this function
                    console.log(deferredRes);

                    //init sound
                    window.appSound = new AppEnv.platformSound();
                    AppEnv.platformSound = undefined, delete AppEnv.platformSound; //clean
                    window.appSound.init(AppEnv.LSKey);
                    window.appSound.setMusicMute(); //toggle the music ON if set by the option or if we need to set default

                    //this.setup.sound.setMute("music");

                    aV.hideLogo();
                    this.reset();
                })
            );

            if (AppEnv.platform != 'android') {
                window.appDeferred.resolve("Loading successful"); //TOSET: proper location of this code when all you want to preload is done
            }
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
            on(document, touch.release, lang.hitch(this, function (event) {
                var res = "App model says: " + this.model.get() + ". SFX is played";
                window.appSound.playSFX("click");
                var int1 = setInterval(function () {
                    window.appSound.playSFX("click");
                }, 750);
                var int2 = setInterval(function () {
                    window.appSound.playSFX("click");
                }, 500);
                setTimeout(function () {
                    clearInterval(int1), clearInterval(int2);
                }, 7000);
                console.log(res);
                this.view.display(res);
            }));
            on(document, "backbutton", lang.hitch(this, function (event) {
                var res = "back btn pressed";
                console.log(res);
                this.view.display(res);
            }));
        }
    });  //declare
});     //define

