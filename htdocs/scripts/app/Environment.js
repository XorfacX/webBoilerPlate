/**
 * Copyright (c) 2013-2016, XorfacX - FairyDwarves
 * Please report to LICENSE.md file.
 */

define(['dojo/_base/declare', "dojo/_base/lang", "app/sound"], function (declare, lang, appSound) {
    _AppEnvCreation = declare(null, {
        constructor: function () {
            //Environment is test
            AppEnv = {
                //TOSET: GENERAL AppEnv definition
                LSKey: "MyAppLSkey",
                platformSound : appSound //sound class, might be extended
            }; //AppEnv

            //TOSET: GENERAL App startup code goes here (will be mixed w platform env before execution)

            //platform url param
            AppEnv.platform = location.search.match(/p=(\w+)/) ? RegExp.$1 : location.search.match(/platform=(\w+)/) ? RegExp.$1 : undefined;

        } //constructor
    });  //declare

});//define
setEnvironment = function () {
    /*return* new*/ _AppEnvCreation();
};
