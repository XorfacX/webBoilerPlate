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

define(['dojo/_base/declare', 'dojo/_base/lang', "dojo/_base/window", "dojo/on", "dojo/dom", "dojox/mobile/Audio", "app/system"], function (declare, lang, win, on, dom, mobAudio, system) {

    /**
    * Sound object
    * Handle everything related to sound (sfx, music, etc)
    *
    * http://www.w3.org/wiki/HTML/Elements/audio for reference
    * Warning check http://html5test.com/ for browser audio type support 
    */
    var sound = declare(null, {
        /** @private */ musicWgt: undefined,
        /** @private */ musicFnL: ["music"], //TOSET: your list of music files here
        supportedFormat: {},
        evl: {},

        Main: undefined,
        Music: undefined,
        SFX: undefined,
        Voice: undefined,
        Video: undefined,

        /**
         * @constructor
         */
        constructor: function () {
            //Test Support
            var testSupport = new mobAudio({
                "source": [],
                id: "supportedFormatTest"
                //"width": 0,
                // "height": 0
            }).placeAt(win.body());
            testSupport.startup();
            var node = dom.byId(supportedFormatTest);
            this.supportedFormat.ogg = (node.canPlayType("audio/ogg") == "probably" || node.canPlayType("audio/ogg") == "maybe");
            this.supportedFormat.aac = (node.canPlayType("audio/aac") == "probably" || node.canPlayType("audio/aac") == "maybe");
            this.supportedFormat.mp3 = (node.canPlayType("audio/mp3") == "probably" || node.canPlayType("audio/mp3") == "maybe");
            this.supportedFormat.wav = (node.canPlayType("audio/wav") == "probably" || node.canPlayType("audio/wav") == "maybe");
            testSupport.destroyRecursive();

            //audio module
            var audioModule = declare(null, {
                /**
                 * 
                 * @constructor
                 */
                constructor: function (id) {
                    this.id = id;
                },
                /** @private @const */ id: undefined,
                /** @private @const */ defaultVol: 100,

                /**
                * Set Volume
                * @param {number} _vol, volume value
                */
                setVolume: function (id, _vol) {
                    var currentVol = this.getVolume();
                    var vol = (typeof _vol != "undefined" ? _vol : currentVol);

                    var option = {}; option[(id ? id : this.id) + "Vol"] = vol;
                    system.LS_optionSet(option);
                },
                /**
                * Get Volume
                * @return {number} the volume value
                */
                getVolume: function (id) {
                    var ret = system.LS_optionGet((id ? id : this.id) + "Vol");
                    if (typeof ret != "number") {
                        ret = this.defaultVol;
                    }
                    return ret;
                },
                /**
                * Set status
                * @param {boolean} _mute, mute status
                */
                setMute: function (id, _mute) {
                    var currentMute = this.getMute();
                    var mute = (typeof _mute != "undefined" ? _mute : currentMute);

                    var option = {}; option[(id ? id : this.id) + "Mute"] = mute;
                    system.LS_optionSet(option);
                },
                /**
                * Get Music status controller
                * @return {string} the mute status
                */
                getMute: function (id) {
                    var ret = system.LS_optionGet((id ? id : this.id) + "Mute");
                    if (typeof ret != "boolean") {
                        ret = false;
                    }
                    return ret;
                }
            });

            var musicWgtModule = declare(audioModule, {
                /**
                * Set Volume
                * @param {number} _vol, volume value
                */
                setVolume: function (id, _vol) {
                    this.inherited(arguments); //call parent w same args
                    musicWgt.domNode.volume = this.getVolume("Main") * this.getVolume("Music") / 10000;
                },
                /**
                * Set status
                * @param {boolean} _mute, mute status
                */
                setMute: function (id, _mute) {
                    this.inherited(arguments); //call parent w same args
                    !this.getMute("Main") && !this.getMute("Music") ? musicWgt.domNode.play() : musicWgt.domNode.pause();
                }
            });

            this.Main = new musicWgtModule("Main");
            this.Music = new musicWgtModule("Music");
            this.SFX = new audioModule("SFX");
            this.Video = new audioModule("Video");
            this.Voice = new audioModule("Voice");
        },

        /**
        * Intialize sound stuff
        */
        init: function (LSKey) {
            try {
                this.LSKey = LSKey; //store the LocalStorage Key for easier access if we need it

                //music widget creation
                musicWgt = new mobAudio({
                    "source": [
                        { src: "audio/" + this.musicFnL[0] + ".ogg", type: "audio/ogg" } //only one song for now
                        //alternative sources
                        //   { src: "audio/music.mp3", type: "audio/mpeg" },
                        //   { src: "audio/music.wav", type: "audio/wav" }
                    ],
                    //autoplay: "autoplay",
                    loop: "loop",
                    id: "musicAudio",
                    preload: 'auto'
                    //"width": 0,
                    // "height": 0
                }).placeAt(win.body());
                musicWgt.startup();

                //initial Volumes
                this.setVolume("Main");
                this.setVolume("Music");
                this.setVolume("SFX");
                this.setVolume("Voice");
                this.setVolume("Video");

                //initial Mutes (music is handled by app constructor)
                this.setMute("Main");
                this.setMute("SFX");
                this.setMute("Voice", true);
                this.setMute("Video", true);

            } catch (error) {
                console.log(error);
            }
        },

        /**
        * Set Volume
        * @param {number} _vol, volume value
        */
        setVolume: function (id, _vol) {
            if (this.hasOwnProperty(id)) {
                this[id].setVolume(id, _vol);
            }
        },
        /**
        * Get Volume
        * @return {number} the volume value
        */
        getVolume: function (id) {
            if (this.hasOwnProperty(id)) {
                return this[id].getVolume(id);
            }
        },
        /**
        * Set status
        * @param {boolean} _mute, mute status
        */
        setMute: function (id, _mute) {
            if (this.hasOwnProperty(id)) {
                this[id].setMute(id, _mute);
            }
        },
        /**
        * Get Music status controller
        * @return {string} the mute status
        */
        getMute: function (id) {
            if (this.hasOwnProperty(id)) {
                return this[id].getMute(id);
            }
        },

        /**
        * Play an SFX by creating an Audio element
        * @param {string} sfxId the filename of the file to play from audio/ folder
        */
        playSFX: function (sfxId) {
            try {
                if (!this.getMute("SFX") && !this.getMute("Main")) { //playing only if both not mutted
                    var srcs = [];
                    if (this.supportedFormat.ogg) { srcs.push({ src: "audio/" + sfxId + ".ogg", type: "audio/ogg" }); }
                    if (this.supportedFormat.aac) { srcs.push({ src: "audio/" + sfxId + ".aac", type: "audio/aac" }); }
                    if (this.supportedFormat.mp3) { srcs.push({ src: "audio/" + sfxId + ".mp3", type: "audio/mp3" }); }
                    if (this.supportedFormat.wav) { srcs.push({ src: "audio/" + sfxId + ".wav", type: "audio/wav" }); }

                    var sfxWgt = new mobAudio({
                        "source": srcs,
                        preload: 'auto',
                        autoplay: "autoplay"
                    }).placeAt(win.body());

                    sfxWgt.domNode.volume = this.getVolume("Main") * this.getVolume("SFX") / 10000;

                    this.evl[sfxWgt.domNode.id] = []; //keep track of event handlers
                    this.evl[sfxWgt.domNode.id].push(on.once(sfxWgt, "ended", lang.hitch(this, this._SFXcleanup, sfxWgt))); //destroy after playback

                    sfxWgt.startup(); //start before handling children error to get them all set

                    //handle error for all srcs.length children
                    for (var i = 0; i < srcs.length; i++) {
                        this.evl[sfxWgt.domNode.id].push(on.once(sfxWgt.domNode.children[i], "error", lang.hitch(this, this._SFXcleanup, sfxWgt)));
                    }
                }
            } catch (e) {
                console.log("error loading file audio/" + sfxId + " - " + e.message);
            }
            //var aud = $('#audio_player').get(0);
            //aud.play();
        },

        /**
        * Clean up an sfx audio widget including its event handlers
        *
        * @param {object} sfxWgt, the widget to cleanup
        * @param {object} e, the event that lead to the cleanup
        * @private
        */
        _SFXcleanup: function (sfxWgt, e) {
            for (var j = 0; j < this.evl[sfxWgt.domNode.id].length; j++) {
                this.evl[sfxWgt.domNode.id][j].remove();
            }
            this.evl[sfxWgt.domNode.id].length = 0;
            delete this.evl[sfxWgt.domNode.id];
            sfxWgt.destroyRecursive();
        }

    }); //end declare
    return new sound();

});     //define
