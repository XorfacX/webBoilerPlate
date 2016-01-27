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
                    alert("cordova loaded ok");

                    document.addEventListener('pause', function () {
                        console.log("pause event detected");
                        alert("pause event detected");
                    }, false);

                    document.addEventListener('resume', function () {
                        console.log("resume event detected");
                        alert("resume event detected");
                    }, false);

                    console.log(Media);
                    platformSound = declare(sound, {
                        ___ANDROIDSOUND___: 1,
                        _pathname: "file:///android_asset/www/audio/",
                        init: function (LSKey) {
                            this.inherited(arguments, [LSKey]); //call superclass init()
                            this.myMedia = //this.musicWgt.source[0].src
                                 new Media(this.musicWgt.source[0].src,
                                    // success callback
                                     function () { console.log("playAudio():Audio Success"); },
                                    // error callback
                                     function (err) { console.log("playAudio():Audio Error: " + err); }
                            );
                            this.myMedia.play();
                            //TODO this is working, we must pause it on pause event
                        }
                    });

                    window.appDeferred.resolve("Loading successful");
                }, false);
            } //constructor
        })();  //declare then execute
    };

});
