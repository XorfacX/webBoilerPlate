"use strict"; //enable strict mode

require([
    'dojo',
    'app/mod1',
    'app/mod2'
], function (dojo, mod1, mod2) {
    var res = "App getting from mod1: '" + (new mod1).get() + "' and from mod 2: '" + (new mod2).get() + "'";
    console.log(res);
    alert(res);
});//require
