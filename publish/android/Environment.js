require([
    "dojo/_base/declare", "dojo/_base/lang", "app/system", "app/sound"
], function (declare, lang, system, sound) {

    setEnvironment = function () {
        declare(_AppEnvCreation, {
            constructor: function () {
                //AppEnv specifics
                system.mixinFull(AppEnv, {
                    //TOSET: platform specifics AppEnv
                    platform: 'android'
                });

                //TODO use dojo.on
                //TOSET: ANDROID specific env code goes here
                document.addEventListener('deviceready', function () {
                    console.log("cordova loaded ok");
                    //alert("cordova loaded ok");

                    document.addEventListener('pause', function () {
                        console.log("pause event detected");
                        alert("pause event detected");
                    }, false);

                    document.addEventListener('resume', function () {
                        console.log("resume event detected");
                        alert("resume event detected");
                    }, false);

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
                                        this._musicMedia.play();
                                    }
                                }
                            );
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
                                            this._SFXcleanup(sfxWgt);
                                        }
                                    }
                                );
                                this._sfxMedias[sfxWgt.domNode.id].play();
                            }
                        },
                        _SFXcleanup: function (sfxWgt, e) {
                            this.inherited(arguments, [sfxWgt, e]); //call superclass _SFXcleanup()
                            this._sfxMedias[sfxWgt.domNode.id].release();
                        }
                        //TODO: this isworking, but do we need to pause/mute on pause event ?
                    });

                    window.appDeferred.resolve("Loading successful");
                }, false);
            } //constructor
        })();  //declare then execute
    };

});
