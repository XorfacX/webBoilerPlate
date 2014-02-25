//http://livedocs.dojotoolkit.org/build/buildSystem
//http://livedocs.dojotoolkit.org/build/qref
//http://dojotoolkit.org/documentation/tutorials/1.9/build/

var dojoP = "../../"; // we start from util/buildscripts
var profile = (function () {
    return {
        basePath: "",
        releaseDir: dojoP + "release",
        releaseName: "dojo_build",

        copyTests: false,
        cssOptimize: "comments",
        layerOptimize: "closure",
        optimize: "closure",
        stripConsole: "normal",
        mini: true,

        //webkitMobile: true, //ENABLE FOR MOBILE

        packages: [{
            name: "dojo",
            location: dojoP + "dojo"
        }, {
            name: "dijit",
            location: dojoP + "dijit"
        }, {
            name: "dojox",
            location: dojoP + "dojox"
        }, {
            name: "app",
            location: dojoP + "app"
        }],

        layers: {
            "dojo/dojo": { //SET YOUR OWN DOJO LAYER HERE
                include: [
                    "dojo/_base/loader",
                    "dojo/i18n",
                    "dojo/domReady",
                    "dojo/on"
                ],
                exclude: [
                    "dojo/parser",
                    "dojo/_base/xhr"
                ],
                customBase: true,
                boot: true
            },
            "app/main": {
                include: [
                    "app/main" //should include others app module
                ],
                exclude: [
                    "dojo/dojo" //to avoid building dojo into the app due to module dependencies
                ]
            }
        }

        //SPECIFY YOUR OWN staticHasFeatures HERE
        //http://dojotoolkit.org/reference-guide/1.9/build/transforms/hasFixup.html#id4
        //http://dojotoolkit.org/documentation/tutorials/1.7/build/
        //https://dojotoolkit.org/documentation/tutorials/1.8/device_optimized_builds/
        //http://dojotoolkit.org/reference-guide/1.9/build/buildSystem.html

        /*
        //Mobile
        staticHasFeatures: {
            "dom-addeventlistener": true,
            "dom-qsa": true,
            "json-stringify": true,
            "json-parse": true,
            "bug-for-in-skips-shadowed": false,
            "dom-matches-selector": true,
            "native-xhr": true,
            "array-extensible": true,
            "ie": undefined,
            "quirks": false,
            "webkit": true
        }
        */

        /*
        //Chrome Packaged
        staticHasFeatures: {
            "dojo-cdn": 0,
            "dojo-loader-eval-hint-url": 0,
            "quirks": 0,
            "dom-quirks": 0,
            "config-dojo-loader-catches": 0,
            "dojo-sniff": 0,
            "dojo-test-sniff": 0,
            "dojo-has-api": 1,
            "dojo-inject-api": 1,
            "dojo-guarantee-console": 0,
            "dojo-firebug": 0,
            "dojo-debug-messages": 0,
            "dojo-dom-ready-api": 1,
            "dojo-config-api": 1,
            "dojo-config-require": 0,
            "dojo-trace-api": 0,
            "dojo-timeout-api": 0,
            "dojo-undef-api": 0,
            "dojo-v1x-i18n-Api": 1,
            "dom": 1,
            "host-browser": 1,
            "extend-dojo": 1,
            "config-tlmSiblingOfDojo": 0,
            "dojo-amd-factory-scan": 0,
            "dojo-combo-api": 0,
            "dojo-modulePaths": 0,
            "dojo-moduleUrl": 0,
            "dojo-publish-privates": 0,
            "dojo-sync-loader": 0,
            "host-node": 0,
            "host-rhino": 0,
            "dojo-force-activex-xhr": 0,
            "json-stringify": 1,
            "json-parse": 1,
            "native-xhr": 1,
            "activex": 0,
            "dojo-unit-tests": 0,
            "dojo-bidi": 0, //http://livedocs.dojotoolkit.org/dojox/mobile/bidi
            "config-bgIframe": 0 //http://dojotoolkit.org/reference-guide/1.9/releasenotes/1.9.html#dijit-backgroundiframe
        }
        */
    };
})();
