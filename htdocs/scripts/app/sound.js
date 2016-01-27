/**
Copyright (c) 2013-2016, XorfacX - FairyDwarves
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
    * Handle everything related to sound (sfxs, music, etc)
    *
    * http://www.w3.org/wiki/HTML/Elements/audio for reference
    * Warning check http://html5test.com/ for browser audio type support 
    */
    return declare(null, {
        /** @private */ musicWgt: undefined,
        /** @private @const */ defaultVol: { main: 100, music: 100, sfxs: 100, video: 100 },
        /** @private */ musicFnL: ["music"],
        supportedFormat: {},
        evl: {},
        _pathname: "audio/",

        /** @constructor */ constructor: function () {
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
        },

        /**
        * Intialize sound stuff
        */
        init: function (LSKey) {
            try {
                this.LSKey = LSKey; //store the LocalStorage Key for easier access

                //music widget creation
                this.musicWgt = new mobAudio({
                    "source": [
                        { src: this._pathname + this.musicFnL[0] + ".ogg", type: "audio/ogg" } //only one song for now
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
                this.musicWgt.startup();

                /**
                 * To be inherited
                 * TODO: not good practice to extend original object i suppose!!
                 */
                this.musicWgt.getVolume = function () {
                    return this.domNode.volume;
                },
                this.musicWgt.setVolume = function (newVol) {
                    this.domNode.volume = newVol;
                },
                this.musicWgt.play = function () {
                    this.domNode.play();
                },
               this.musicWgt.pause = function () {
                    this.domNode.pause();
                },
                this.musicWgt.stop = function () {
                    this.domNode.stop();
                },
               this.musicWgt.release = function () {
                };

                //initial Volumes
                this.setMainVolume();
                this.setMusicVolume();
                this.setSFXsVolume();

                //initial Mutes (music is handled by app constructor)
                this.setMainMute();
                this.setSFXsMute();

            } catch (error) {
                console.log(error);
            }
        },

        /**
        * Set Music Volume controller
        * @param {number} _vol, volume value
        */
        setMusicVolume: function (_vol) {
            var currentVol = this.getMusicVolume();
            var vol = (typeof _vol != "undefined" ? _vol : (typeof currentVol != "undefined" ? currentVol : this.defaultVol.main));

            system.LS_optionSet(this.LSKey, { "MucicVol": vol });
            this.musicWgt.setVolume(this.getMainVolume() * vol / 10000);
        },
        /**
        * Get Music Volume controller
        * @return {number} the volume value
        */
        getMusicVolume: function () {
            var ret = system.LS_optionGet(this.LSKey, "MucicVol");
            if (typeof ret != "number") {
                ret = this.defaultVol.music;
            }
            return ret;
        },
        /**
        * Set Music status controller
        * @param {boolean} _mute, mute status
        */
        setMusicMute: function (_mute) {
            var currentMute = this.getMusicMute();
            var mute = (typeof _mute != "undefined" ? _mute : (typeof currentMute != "undefined" ? currentMute : false));

            system.LS_optionSet(this.LSKey, { "MusicMute": mute });
            !mute && !this.getMainMute() ? this.musicWgt.play() : this.musicWgt.pause();
        },
        /**
        * Get Music status controller
        * @return {string} the mute status
        */
        getMusicMute: function () {
            var ret = system.LS_optionGet(this.LSKey, "MusicMute");
            if (typeof ret != "boolean") {
                ret = false;
            }
            return ret;
        },

        /**
        * Set SFXs Volume controller
        * @param {number} _vol, volume value
        */
        setSFXsVolume: function (_vol) {
            var currentVol = this.getSFXsVolume();
            var vol = (typeof _vol != "undefined" ? _vol : (typeof currentVol != "undefined" ? currentVol : this.defaultVol.sfxs));

            system.LS_optionSet(this.LSKey, { "SFXsVol": vol });
        },
        /**
        * Get SFXs Volume controller
        * @return {number} the volume value
        */
        getSFXsVolume: function () {
            var ret = system.LS_optionGet(this.LSKey, "SFXsVol");
            if (typeof ret != "number") {
                ret = this.defaultVol.sfxs;
            }
            return ret;
        },
        /**
        * Set SFXs status controller
        * @param {boolean} _mute, mute status
        */
        setSFXsMute: function (_mute) {
            var currentMute = this.getSFXsMute();
            var mute = (typeof _mute != "undefined" ? _mute : (typeof currentMute != "undefined" ? currentMute : false));

            system.LS_optionSet(this.LSKey, { "SFXsMute": mute });
        },
        /**
        * Get SFXs status controller
        * @return {string} the mute status
        */
        getSFXsMute: function () {
            var ret = system.LS_optionGet(this.LSKey, "SFXsMute");
            if (typeof ret != "boolean") {
                ret = false;
            }
            return ret;
        },

        /**
        * Set Main Volume controller
        * @param {number} _vol, volume value
        */
        setMainVolume: function (_vol) {
            var currentVol = this.getMainVolume();
            var vol = (typeof _vol != "undefined" ? _vol : (typeof currentVol != "undefined" ? currentVol : this.defaultVol.main));

            system.LS_optionSet(this.LSKey, { "MainVol": vol });
            this.musicWgt.setVolume(this.getMusicVolume() * vol / 10000);
        },
        /**
        * Get Main Volume controller
        * @return {number} the volume value
        */
        getMainVolume: function () {
            var ret = system.LS_optionGet(this.LSKey, "MainVol");
            if (typeof ret != "number") {
                ret = this.defaultVol.main;
            }
            return ret;
        },
        /**
        * Set Main status controller
        * @param {boolean} _mute, mute status
        */
        setMainMute: function (_mute) {
            var currentMute = this.getMainMute();
            var mute = (typeof _mute != "undefined" ? _mute : (typeof currentMute != "undefined" ? currentMute : false));

            system.LS_optionSet(this.LSKey, { "MainMute": mute });
            !mute && !this.getMusicMute() ? this.musicWgt.play() : this.musicWgt.pause(); //handle music
        },
        /**
        * Get Main status controller
        * @return {string} the mute status
        */
        getMainMute: function () {
            var ret = system.LS_optionGet(this.LSKey, "MainMute");
            if (typeof ret != "boolean") {
                ret = false;
            }
            return ret;
        },


        /**
        * Play an SFX by creating an Audio element
        * @param {string} sfxId the filename of the file to play from audio/ folder
        */
        playSFX: function (sfxId) {
            try {
                if (!this.getSFXsMute() && !this.getMainMute()) { //playing only if both not mutted
                    var srcs = [];
                    if (this.supportedFormat.ogg) { srcs.push({ src: this._pathname + sfxId + ".ogg", type: "audio/ogg" }); }
                    if (this.supportedFormat.aac) { srcs.push({ src: this._pathname + sfxId + ".aac", type: "audio/aac" }); }
                    if (this.supportedFormat.mp3) { srcs.push({ src: this._pathname + sfxId + ".mp3", type: "audio/mp3" }); }
                    if (this.supportedFormat.wav) { srcs.push({ src: this._pathname + sfxId + ".wav", type: "audio/wav" }); }

                    var sfxWgt = new mobAudio({
                        "source": srcs,
                        preload: 'auto',
                        autoplay: "autoplay"
                    }).placeAt(win.body());

                    /**
                     * To be inherited
                     */
                    sfxWgt.getVolume = function () {
                        return this.domNode.volume;
                    },
                    sfxWgt.setVolume = function (newVol) {
                        this.domNode.volume = newVol;
                    },
                    sfxWgt.play = function () {
                        this.domNode.play();
                    },
                    sfxWgt.pause = function () {
                        this.domNode.pause();
                    },
                    sfxWgt.stop = function () {
                        this.domNode.stop();
                    },
                    sfxWgt.release = function () {
                    };

                    sfxWgt.domNode.volume = this.getMainVolume() * this.getSFXsVolume() / 10000;

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
        * @param {widget} sfxWgt, the widget to cleanup
        * @param {event} e, the event that lead to the cleanup
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

    }); //end declare and run

});     //define