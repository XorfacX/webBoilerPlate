var isTestRe = /\/tests\//;
var profile = {
    resourceTags: {
        test: function (filename, mid) {
            return isTestRe.test(filename);
        },

        amd: function (filename, mid) {
            return /\.js$/.test(filename);
        }
    }
};
