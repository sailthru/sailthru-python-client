const {test} = require('node:test');
const assert = require('node:assert/strict');
const discover = require('./runtime-matrix.cjs');

async function resolve(releases) {
  let output;
  await discover({
    core: {info() {}, setOutput(name, value) {
      assert.equal(name, 'versions');
      output = JSON.parse(value);
    }},
    fetch: async () => ({ok: true, json: async () => releases})
  });
  return output;
}

test('includes intermediate and future stable releases, excludes prereleases and duplicates', async () => {
  const releases = [
    ...Array.from({length: 8}, (_, index) => ({version: `3.${index + 10}.0`, stable: true})),
    {version: '3.15.1', stable: true}, {version: '3.18.0rc1', stable: false},
    {version: '3.19.0', stable: false}, {version: '4.0.0', stable: true}
  ];
  assert.deepEqual(await resolve(releases), ['3.11', '3.12', '3.13', '3.14', '3.15', '3.16', '3.17', '4.0']);
});

test('fails rather than quietly running an empty or incomplete matrix', async () => {
  await assert.rejects(resolve([]));
  await assert.rejects(resolve([{version: '4.0.0', stable: true}]));
  await assert.rejects(resolve(null));
});

test('metadata HTTP, JSON and network failures fail discovery without emitting a matrix', async () => {
  const core = {info() {}, setOutput() {assert.fail('Must not emit a fallback matrix');}};
  await assert.rejects(discover({core, fetch: async () => ({ok: false, status: 503})}), /503/);
  await assert.rejects(discover({core, fetch: async () => ({
    ok: true, json: async () => {throw new SyntaxError('Invalid JSON');}
  })}), /Invalid JSON/);
  await assert.rejects(discover({core, fetch: async () => {throw new Error('Network failure');}}), /Network failure/);
});
