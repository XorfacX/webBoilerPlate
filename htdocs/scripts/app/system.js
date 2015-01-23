/**
Copyright (c) 2013-2015, XorfacX - FairyDwarves
All rights reserved.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

define(['dojo/_base/declare'], function (declare) {

    /**
    * Sytem object with all useful common functions incl Local storage management
    */
    var system = declare(null, {
        /** @public */ LSKey: "__ProjectLSKey__", //TODO: replace it

        /**
         * Mixin two objects with nested properties
         * The second one into the first one
         * 
         * @param obj1 {object}, object merging into
         * @param obj2 {object}, object merged
         * 
         * @return {object} the merged object
         */
        mixinFull: function (obj1, obj2) {
            for (var p in obj2) {
                if (obj2.hasOwnProperty(p)) {
                    try {
                        // Property in destination object set; update its value.
                        if (obj2[p].constructor == Object) {
                            obj1[p] = this.mixinFull(obj1[p], obj2[p]);

                        } else {
                            obj1[p] = obj2[p];
                        }

                    } catch (e) {
                        // Property in destination object not set; create it and set its value.
                        obj1[p] = obj2[p];
                    }
                }
            }
            return obj1;
        },

        /**
        * generate a int random number in [min, max]
        * random(min,min) returns min
        * random(max,min) = random (min, max)
        * WARNING: no type check on params has it's a basic function
        *
        * @param {number} min, the lower border
        * @param {number} max, the higher border
        * @return {number} the random generated number
        */
        random: function (min, max) {
            return Math.floor(Math.random() * (1 + Math.abs(max - min))) + Math.min(min, max);
        },

        /**
        * Check if localStorage is available
        * NB: could be disabled (cookies not accepted, some private browsing mode, chrome new packaged app, IE file:// websites, ...) or non present (old browsers)
        */
        hasLocalStorage: function () {
            var t = '__FDlsTest__';
            try {
                localStorage.setItem(t, t);
                localStorage.removeItem(t);
                return true;
            } catch (e) {
                return false;
            }
        },

        /**
        * Get the LocalStorage formatted into an object
        * @return {*} the LocalStorage formatted into an object, false otherwise
        */
        LS_get: function () {
            return (localStorage && localStorage[this.LSKey]) ? JSON.parse(localStorage[this.LSKey]) : false;
        },

        /**
        * Erase the whole localStorage
        */
        LS_erase: function () {
            delete localStorage[this.LSKey];
        },

        /**
        * Save an option into LS
        *
        * @param optionVals {object} list object of optionsto save
        * 
        * @return {boolean} true if ok, false otherwise
        */
        LS_optionSet: function (optionVals) {
            var ret = false;
            if (this.hasLocalStorage()) {
                if (!localStorage[this.LSKey]) {
                    localStorage[this.LSKey] = JSON.stringify({ options: {} });
                }

                var LSo = JSON.parse(localStorage[this.LSKey]);
                if (!LSo.options) {
                    LSo.options = {};
                }

                for (var option in optionVals) {
                    if (optionVals.hasOwnProperty(option)) {
                        LSo.options[option] = optionVals[option];
                    }
                }

                ret = true;
                localStorage[this.LSKey] = JSON.stringify(LSo);
            }

            return ret;
        },

        /**
        * Get an option value from LS
        *
        * @param optionName {string}, the option to get, if none return the whole option object
        * 
        * @return {(string|undefined)} the option value, undef otherwise
        */
        LS_optionGet: function (optionName) {
            var ret = undefined;
            if (this.hasLocalStorage()) {
                if (localStorage[this.LSKey]) {
                    var LSo = JSON.parse(localStorage[this.LSKey]);
                    if (LSo.options) {
                        if (typeof optionName != "undefined") {
                            if (typeof LSo.options[optionName] != "undefined") {
                                return LSo.options[optionName];
                            }
                        } else {
                            return LSo.options;
                        }
                    }
                }
            }
            return ret;
        }

    }); //end declare
    return new system();

});     //define
