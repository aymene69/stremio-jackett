#!/usr/bin/env node
import pkg from 'stremio-addon-sdk';
const { serveHTTP } = pkg;

import addonInterface from './addon.js';
// The import does not need curly braces since it's the default export

serveHTTP(addonInterface, { port: process.env.PORT || 59803 });


// when you've deployed your addon, un-comment this line
// publishToCentral("https://my-addon.awesome/manifest.json")
// for more information on deploying, see: https://github.com/Stremio/stremio-addon-sdk/blob/master/docs/deploying/README.md
