require([
    "dojo/_base/declare", "dojo/_base/lang"
], function (declare, lang) {

    setEnvironment = function () {
        declare(_AppEnvCreation, {
            constructor: function () {
                //AppEnv specifics
                lang.mixin(AppEnv, {
                    //TOSET: platform specifics AppEnv
                    platform: 'facebook'
                });

                /*TODO uncomment if useful
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
                ga('linker:autoLink', [AppEnv.backendURL.match(/^https?\:\/\/(?:www\.)?([^\/?#]+)(?:[\/?#]|$)/i)[1], AppEnv.backendURL]); //add both coz i duno which one works */

                //TOSET: platform specifics startup code

            } //constructor
        })();  //declare then execute
    };

});
