FDwebRoot
===

The project aim is to be the root of all FD web project.
It contains the structure and scripts design to start a project with a proper configuration.

It uses:
* javascript framework: dojo
* script tool: waf
* build tool: closure compiler
* build scripts: dojo.profile.js and app.profile.js which must be updated to fit your project


HowTo
---
./waf configure --download
./waf build
./waf distclean


Dependencies
---
Python >2.6 <3 to be able to execute waf script (TODO update to python 3)