require([
    "dojo/_base/declare", "dojo/_base/lang", "dojo/on", "app/system", "app/sound"
], function (declare, lang, on, system, sound) {

    setEnvironment = function () {
        declare(_AppEnvCreation, {
            constructor: function () {
                //AppEnv specifics
                system.mixinFull(AppEnv, {
                    //TOSET: platform specifics AppEnv
                    platform: 'android'
                });

                //TOSET: ANDROID specific env code goes here
                on(document, "deviceready", lang.hitch(this, function (event) {
                    console.log("cordova loaded ok");

                    on(document, "pause", lang.hitch(this, function (event) {
                        console.log("pause event detected");
                    }));

                    on(document, "resume", lang.hitch(this, function (event) {
                        console.log("resume event detected");
                    }));

                    var context;
                    platformSound = declare(sound, {
                        ___ANDROIDSOUND___: 1,
                        _pathname: "file:///android_asset/www/audio/",
                        _musicMedia: undefined,

                        constructor: function () {
                            context = this;
                        },

                        init: function (LSKey) {
                            this.inherited(arguments, [LSKey]); //call superclass init()
                            this._musicMedia = new Media(this.musicWgt.source[0].src,
                                function () {
                                    console.log("Music Success");
                                },
                                function (err) {
                                    console.log("Music Error: " + err);
                                },
                                function (status) { //LOOP the music
                                    if (status === Media.MEDIA_STOPPED) {
                                        this.play();
                                    }
                                }
                            ); //CALLBACKS NOT WORKING: cordova.plugin.media bug @https://issues.apache.org/jira/browse/CB-10476
                            this.musicWgt.setVolume = function (newVol) {
                                context._musicMedia.setVolume(newVol); //between 0.0 and 1.0
                            },
                            this.musicWgt.play = function () {
                                context._musicMedia.play();
                            },
                            this.musicWgt.pause = function () {
                                context._musicMedia.pause();
                            },
                            this.musicWgt.stop = function () {
                                context._musicMedia.stop();
                            },
                            this.musicWgt.release = function () {
                                context._musicMedia.release();
                            };
                            //on(document, "startPlayingAudio, stopPlayingAudio, pausePlayingAudio, release, status", lang.hitch(this, function (event) {
                            //    console.log("Media event: " + JSON.stringify(event));
                            //}));

                            //this._musicMedia.play();
                            //TODO music should start be mute is not working...
                            //TODO music is not looping
                            //TODO this is working, we must pause it on pause event though and resume it when needed!!
                        },

                        _sfxMedias: {},
                        playSFX: function (sfxId) {
                            var sfxWgt = this.inherited(arguments, [sfxId]); //call superclass playSFX()
                            if (typeof sfxWgt != "undefined") {
                                this._sfxMedias[sfxWgt.domNode.id] = new Media(sfxWgt.source[0].src,
                                    function () {
                                        console.log("SFX " + sfxId + " Success");
                                    },
                                    function (err) {
                                        console.log("SFX " + sfxId + " Error: " + err);
                                        //TODO maybe cleanup here ?
                                    },
                                    function (status) { //clean on finish
                                        if (status === Media.MEDIA_STOPPED) {
                                            lang.hitch(context, context._SFXcleanup, sfxWgt)();
                                        }
                                    }
                                );
                                this._sfxMedias[sfxWgt.domNode.id].play();
                            }
                        },
                        _SFXcleanup: function (sfxWgt, e) {
                            this._sfxMedias[sfxWgt.domNode.id].release(); //before calling parent coz after the widget is destroyed
                            this.inherited(arguments, [sfxWgt, e]); //call superclass _SFXcleanup()
                        }
                        //TODO: this isworking, but do we need to pause/mute on pause event ?
                    });

                    window.appDeferred.resolve("Loading successful");
                }));
            } //constructor
        })();  //declare then execute
    };

});
