setEnvironment = function () {
    require([
       "dojo/_base/declare", "dojo/_base/lang", "dojo/dom", "FDGE/main"
    ], function (declare, lang, dom, fdge) {
        var android_env = declare(_AppEnvCreation, {
            constructor: function () {
                //TOSET: ANDROID specific env code goes here

            } //constructor
        });  //declare
        android_env();
    });
};
