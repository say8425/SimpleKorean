const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');

const {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  promptCandidates,
  readFirstFile,
  skillPath,
  stripFrontmatter,
} = require('./simple-korean-activate');

const SCRIPT = path.join(__dirname, 'simple-korean-activate.js');
const REPO_PROMPT = path.join(__dirname, '..', '..', 'prompts', 'system-prompt.md');

function tmpRoot(promptText) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-hook-'));
  fs.mkdirSync(path.join(root, 'prompts'));
  if (promptText !== undefined) {
    fs.writeFileSync(path.join(root, 'prompts', 'system-prompt.md'), promptText);
  }
  return root;
}

function runHook(env) {
  return spawnSync(process.execPath, [SCRIPT], { env: { ...process.env, PLUGIN_ROOT: '', CLAUDE_PLUGIN_ROOT: '', ...env }, encoding: 'utf8' });
}

test('플러그인 루트의 프롬프트를 먼저 읽는다', () => {
  assert.equal(promptCandidates('/plugin', '/plugin/src/hooks')[0], '/plugin/prompts/system-prompt.md');
});

test('플러그인 루트가 없으면 레포 구조로 찾는다', () => {
  assert.equal(promptCandidates(undefined, '/repo/src/hooks')[0], '/repo/prompts/system-prompt.md');
});

test('읽을 수 없는 후보는 건너뛰고 다음 후보를 읽는다', (t) => {
  if (process.getuid && process.getuid() === 0) {
    t.skip('root는 권한 000 파일도 읽는다');
    return;
  }
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-read-'));
  const locked = path.join(dir, 'locked.md');
  const open = path.join(dir, 'open.md');
  fs.writeFileSync(locked, 'SECRET');
  fs.chmodSync(locked, 0o000);
  fs.writeFileSync(open, 'OPEN');
  assert.equal(readFirstFile([locked, open]), 'OPEN');
  fs.chmodSync(locked, 0o644);
});

test('디렉터리 후보는 건너뛴다', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-dir-'));
  const asDir = path.join(dir, 'system-prompt.md');
  fs.mkdirSync(asDir);
  const file = path.join(dir, 'real.md');
  fs.writeFileSync(file, 'REAL');
  assert.equal(readFirstFile([asDir, file]), 'REAL');
});

test('모든 후보가 실패하면 빈 문자열이다', () => {
  assert.equal(readFirstFile(['/nonexistent/a.md', '/nonexistent/b.md']), '');
});

test('LF와 CRLF frontmatter를 지운다', () => {
  assert.equal(stripFrontmatter('---\nname: x\n---\nBody'), 'Body');
  assert.equal(stripFrontmatter('---\r\nname: x\r\n---\r\nBody'), 'Body');
});

test('프롬프트가 없으면 대체 규칙을 보낸다', () => {
  assert.equal(buildContext(''), FALLBACK_CONTEXT);
});

test('레포의 프롬프트는 상한 안에 들고 규칙 블록만 나간다', () => {
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'));
  assert.ok(out.length <= MAX_CHARS, `${out.length} > ${MAX_CHARS}`);
  assert.ok(out.startsWith('SIMPLE KOREAN 스킬이 자동으로 켜졌습니다'));
  assert.ok(out.includes('답변(모든 모드의 채팅 답변)'));
  assert.ok(out.includes('레포지토리'));
  assert.ok(!out.includes('# 시스템 프롬프트'), '페이지 제목이 섞였다');
  assert.ok(!out.includes('짧은 판본'), '짧은 판본이 섞였다');
  assert.ok(!out.includes('붙여 넣으세요'), '안내 문단이 섞였다');
});

function withSkill(root) {
  fs.mkdirSync(path.join(root, 'skills', 'simple-korean'), { recursive: true });
  fs.writeFileSync(path.join(root, 'skills', 'simple-korean', 'SKILL.md'), 'S');
  return root;
}

test('찾은 SKILL.md와 규칙 목록의 절대 경로를 알린다', () => {
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'), '/plugin/skills/simple-korean/SKILL.md');
  assert.ok(out.includes('적용한 규칙의 번호를 적어야 하면 먼저 이 파일을 읽으세요: /plugin/skills/simple-korean/SKILL.md.'));
  assert.ok(out.includes('/plugin/skills/simple-korean/references/rule-catalog.md에 있는 번호만 쓰세요'));
});

test('SKILL.md를 찾지 못하면 상대 경로로 알린다', () => {
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'));
  assert.ok(out.includes('먼저 이 플러그인의 skills/simple-korean/SKILL.md를 읽으세요.'));
});

test('플러그인 루트의 SKILL.md를 먼저 찾고, 없으면 빈 문자열이다', () => {
  const root = withSkill(tmpRoot('P'));
  assert.equal(skillPath(root, '/nowhere/src/hooks'), path.join(root, 'skills', 'simple-korean', 'SKILL.md'));
  assert.equal(skillPath(undefined, '/nowhere/src/hooks'), '');
});

test('긴 설치 경로에서도 상한 안에 든다', () => {
  const long = `/${'a'.repeat(200)}/skills/simple-korean/SKILL.md`;
  const out = buildContext(fs.readFileSync(REPO_PROMPT, 'utf8'), long);
  assert.ok(out.length <= MAX_CHARS, `${out.length} > ${MAX_CHARS}`);
  assert.ok(out.includes(long));
});

test('상한을 넘는 프롬프트는 중간에 자르지 않고 대체 규칙으로 바꾼다', () => {
  assert.equal(buildContext('x'.repeat(MAX_CHARS + 1)), FALLBACK_CONTEXT);
});

test('main()은 CLAUDE_PLUGIN_ROOT의 프롬프트를 읽는다', () => {
  const r = runHook({ CLAUDE_PLUGIN_ROOT: tmpRoot('CLAUDE-COPY') });
  assert.equal(r.status, 0);
  assert.ok(r.stdout.includes('CLAUDE-COPY'));
});

test('main()은 플러그인 루트의 SKILL.md 절대 경로를 알린다', () => {
  const root = withSkill(tmpRoot('BODY'));
  const r = runHook({ CLAUDE_PLUGIN_ROOT: root });
  assert.equal(r.status, 0);
  assert.ok(r.stdout.includes(path.join(root, 'skills', 'simple-korean', 'SKILL.md')));
});

test('main()은 PLUGIN_ROOT(Codex)의 프롬프트를 읽는다', () => {
  const r = runHook({ PLUGIN_ROOT: tmpRoot('CODEX-COPY') });
  assert.equal(r.status, 0);
  assert.ok(r.stdout.includes('CODEX-COPY'));
});

test('main()은 후보가 하나도 없으면 대체 규칙을 내고 0으로 끝난다', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sk-main-'));
  const script = path.join(dir, 'a', 'b', 'hook.js');
  fs.mkdirSync(path.dirname(script), { recursive: true });
  fs.copyFileSync(SCRIPT, script);
  const root = tmpRoot(undefined);
  const r = spawnSync(process.execPath, [script], { env: { ...process.env, PLUGIN_ROOT: '', CLAUDE_PLUGIN_ROOT: root }, encoding: 'utf8' });
  assert.equal(r.status, 0);
  assert.equal(r.stdout, FALLBACK_CONTEXT);
});
