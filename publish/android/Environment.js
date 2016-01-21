require([
    "dojo/_base/declare", "dojo/_base/lang", "app/system"
], function (declare, lang, system) {

    setEnvironment = function () {
        declare(_AppEnvCreation, {
            constructor: function () {
                //AppEnv specifics
                system.mixinFull(AppEnv, {
                    //TOSET: platform specifics AppEnv
                    platform: 'android'
                });

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
                }, false);
            } //constructor
        })();  //declare then execute
    };

});
