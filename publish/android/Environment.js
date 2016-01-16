setEnvironment = function () {
    require([
       "dojo/_base/declare", "dojo/_base/lang", "dojo/dom", "FDGE/main"
    ], function (declare, lang, dom, fdge) {
        var android_env = declare(_AppEnvCreation, {
            constructor: function () {
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
        });  //declare
        android_env();
    });
};
