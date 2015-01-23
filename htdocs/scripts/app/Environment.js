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

define(['dojo/_base/declare', "dojo/_base/lang"], function (declare, lang) {
    _AppEnvCreation = declare(null, {
        constructor: function () {
            //Environment is test
            AppEnv = {
                //TOSET: GENERAL AppEnv definition
                LSKey: "MyAppLSkey",
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
