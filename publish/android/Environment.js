require([
    "dojo/_base/declare", "dojo/_base/lang", "dojo/on", "dojo/Deferred", "app/system", "app/sound"
], function (declare, lang, on, Deferred, system, sound) {

    setEnvironment = function () {
        declare(_AppEnvCreation, {
            constructor: function () {
                //AppEnv specifics
                system.mixinFull(AppEnv, {
                    //TOSET: platform specifics AppEnv
                    platform: 'android'
                });

                //update backend location for modules
                require({ paths: { backend: AppEnv.backendPath + 'scripts' } });

                //Google Anaylitics (nb: after mixin to get good url)
                (function (i, s, o, g, r, a, m) {
                    i['GoogleAnalyticsObject'] = r; i[r] = i[r] || function () {
                        (i[r].q = i[r].q || []).push(arguments)
                    }, i[r].l = 1 * new Date(); a = s.createElement(o),
                    m = s.getElementsByTagName(o)[0]; a.async = 1; a.src = g; m.parentNode.insertBefore(a, m)
                })(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');

                ga('create', 'UA-XXXXXXXX-X', 'auto'); //TOSET: proper GA ID here if u want to use it
                ga('require', 'displayfeatures'); //https://support.google.com/analytics/answer/2444872?hl=en&utm_id=ad
                ga('send', 'pageview');

                ga('require', 'linker');
                ga('linker:autoLink', [AppEnv.backendURL.match(/^https?\:\/\/(?:www\.)?([^\/?#]+)(?:[\/?#]|$)/i)[1], AppEnv.backendURL]); //add both coz i duno which one works


                //TOSET: ANDROID specific env code goes here
                window.envDeferred = new Deferred();
                var devicereadyEVL = on(document, "deviceready", lang.hitch(this, function (event) {
                    console.log("cordova loaded ok");

                    // Pause event handling
                    on(document, "pause", lang.hitch(this, function (event) {
                        console.log("pause event detected");
                        window.appSound.onPauseEVH();
                    }));

                    //resume event handling
                    on(document, "resume", lang.hitch(this, function (event) {
                        console.log("resume event detected");
                        window.appSound.onResumeEVH();
                    }));

                    //back button event handling
                    on(document, "backbutton", lang.hitch(this, function (event) {
                        console.log("backbutton event detected");
                        if (typeof window.appSound != "undefined") {
                            window.appSound.playSFX("fdge_btn_click"); //will cause an error on sound file non present but wont block anything
                        }
                    }));

                    //inapp browser plugin setup
                    if (cordova.InAppBrowser) {
                        window.open = cordova.InAppBrowser.open;
                    }

                    /**
                     * Sound handling using cordova media plugin, https://www.npmjs.com/package/cordova-plugin-media
                     */
                    if (typeof Media != "undefined") {
                        AppEnv.platformSound = declare(sound, {
                            ___ANDROIDSOUND___: 1,
                            _pathname: "file:///android_asset/www/audio/",
                            _musicMedia: undefined,
                            _musicStatus: undefined,
                            _musicStatusBkp: undefined,

                            constructor: function () {
                            },

                            init: function (LSKey) {
                                this.inherited(arguments, [LSKey]); //call superclass init()
                                if (this.musicWgt.source.length > 0) {
                                    this._musicMedia = new Media(this.musicWgt.source[0].src,
                                        lang.hitch(this, function () {
                                            console.log("Music Success");
                                        }),
                                        lang.hitch(this, function (err) {
                                            console.log("Music Error: code " + err.code + (typeof err.msg != "undefined" ? ', msg: ' + err.msg : ''));
                                            this.release();
                                        }),
                                        lang.hitch(this, function (status) {
                                            this._musicStatus = status;
                                            if (status === Media.MEDIA_STOPPED) { //LOOP the music
                                                this.play();
                                            }
                                        })
                                    );
                                    this.musicWgt.setVolume = lang.hitch(this, function (newVol) {
                                        this._musicMedia.setVolume(newVol); //between 0.0 and 1.0
                                    }),
                                    this.musicWgt.play = lang.hitch(this, function () {
                                        this._musicMedia.play();
                                    }),
                                    this.musicWgt.pause = lang.hitch(this, function () {
                                        this._musicMedia.getCurrentPosition(
                                            lang.hitch(this, function (position) {
                                                if (position > 0) {
                                                    this._musicMedia.pause();
                                                }
                                            }),
                                            lang.hitch(this, function (err) { //error callback
                                                console.log("Music::pause(), error getting position" + err);
                                            }));
                                    }),
                                    this.musicWgt.stop = lang.hitch(this, function () {
                                        this._musicMedia.stop();
                                    }),
                                    this.musicWgt.release = lang.hitch(this, function () {
                                        this._musicMedia.release();
                                    });
                                    //on(document, "startPlayingAudio, stopPlayingAudio, pausePlayingAudio, release, status", lang.hitch(this, function (event) {
                                    //    console.log("Media event: " + JSON.stringify(event));
                                    //}));

                                    //this._musicMedia.play();
                                    //TODO(future) music should start muted, it's not working...
                                }
                            },

                            /**
                             * Cordova Pause Event Handler
                             */
                            onPauseEVH: function () {
                                this._musicStatusBkp = this._musicStatus; //backup music status to restore on resume
                                if (this._musicStatus === Media.STARTING || this._musicStatus === Media.MEDIA_RUNNING) { //pause if it is playing, otherwise do nothing
                                    this.musicWgt.pause();
                                }
                                //NB: doesn't seems we need to pause SFXs.
                            },
                            /**
                             * Cordova Resume Event Handler
                             */
                            onResumeEVH: function () {
                                if (typeof this._musicStatusBkp != "undefined" && (this._musicStatusBkp === Media.STARTING || this._musicStatusBkp === Media.MEDIA_RUNNING)) { //play if it was playing, otherwise do nothing
                                    this.musicWgt.play(); //this will update _musicStatus
                                }
                                this._musicStatusBkp = undefined; //in all cases remove backup status
                            },

                            //we replace app.sound by proper Media handling functions
                            _sfxMedias: {},
                            playSFX: function (sfxId) {
                                //create a unique sfx media key
                                var sfxKey = sfxId + system.random(100000, 1000000);
                                while (typeof this._sfxMedias[sfxKey] != "undefined") {
                                    sfxKey = sfxId + system.random(100000, 1000000);
                                }

                                //create the sfx media then store it
                                this._sfxMedias[sfxKey] = new Media(this._pathname + sfxId + ".ogg",
                                    lang.hitch(this, function () {
                                        console.log("SFX " + sfxId + " Play Success");
                                        setTimeout(lang.hitch(this, this._SFXcleanup, sfxKey), Math.ceil(this._sfxMedias[sfxKey].getDuration() * 100 + 0.01) * 10);
                                    }),
                                    lang.hitch(this, function (err) {
                                        console.log("SFX " + sfxId + " Error: code " + err.code + (typeof err.msg != "undefined" ? ', msg: ' + err.msg : ''));
                                        lang.hitch(this, this._SFXcleanup, sfxKey)();
                                    })
                                );

                                //play the sfx media
                                this._sfxMedias[sfxKey].play();
                            },
                            _SFXcleanup: function (sfxKey, e) {
                                this._sfxMedias[sfxKey].release(); //release system's audio resources (mandatory)
                                delete this._sfxMedias[sfxKey];
                            }
                        });
                    }

                    window.envDeferred.resolve("Android env Loaded successfully");
                    if (devicereadyEVL) {
                        devicereadyEVL.remove();
                    }
                }));
            } //constructor
        })();  //declare then execute
    };

});
