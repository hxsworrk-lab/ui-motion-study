import {readFile, writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const local = new URL('./', import.meta.url);
const plugin = await readFile(new URL('hx-form-probe.php', local), 'utf8');
const exercise = await readFile(new URL('exercise.php', local), 'utf8');
const blueprint = {
  $schema: 'https://playground.wordpress.net/blueprint-schema.json',
  // The first observed run selected "latest", which resolved to 7.1.3.
  // This pins subsequent reproduction to that actual observed core version.
  preferredVersions: {php: '8.3', wp: '7.1.3'},
  steps: [
    {step: 'writeFile', path: '/wordpress/wp-content/plugins/hx-form-probe.php', data: plugin},
    {step: 'activatePlugin', pluginPath: 'hx-form-probe.php'},
    {step: 'runPHP', code: exercise},
  ],
};
const output = process.argv[2];
if (!output) throw new Error('Supply an isolated output blueprint path.');
await writeFile(output, JSON.stringify(blueprint, null, 2) + '\n');
console.log(`Blueprint generated from ${fileURLToPath(local)}; no client material or external files.`);
