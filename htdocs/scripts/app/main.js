"use strict"; //enable strict mode

require([
    'dojo/on',
    'app/mod1',
    'app/mod2'
], function (on, mod1, mod2) {
    on(document, "click", function () {
        var res = "App getting from mod1: '" + (new mod1).get() + "' and from mod 2: '" + (new mod2).get() + "'";
        console.log(res);
        alert(res);
    });
});//require
