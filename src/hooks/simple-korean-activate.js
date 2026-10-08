#!/usr/bin/env node

const fs = require('node:fs');
const path = require('node:path');

// Claude Code는 훅 표준 출력을 10,000자까지만 받는다. 넘으면 파일로 빠지고 미리 보기만 전달된다.
const MAX_CHARS = 9500;

const FALLBACK_CONTEXT = `SIMPLE KOREAN 스킬이 자동으로 켜졌습니다

기술 문서를 쓸 때 쉬운 한국어 규칙을 따르세요. 문장을 짧게 쓰고, 조건을 명령 앞에 두고, 한 단어에 한 뜻만 주세요. 코드, 식별자, 명령, 인용한 오류 문구는 바꾸지 마세요.`;

// 모델은 플러그인이 어디에 설치됐는지 모른다. 찾은 SKILL.md의 절대 경로를 알려 줘야 그 파일과
// 규칙 목록을 읽는다. 찾지 못하면 상대 경로로 알린다.
function header(skillPath) {
  const where = skillPath
    ? `먼저 이 파일을 읽으세요: ${skillPath}. 규칙 번호는 ${path.join(path.dirname(skillPath), 'references', 'rule-catalog.md')}에 있는 번호만 쓰세요.`
    : '먼저 이 플러그인의 skills/simple-korean/SKILL.md를 읽으세요. 규칙 번호는 그 옆의 references/rule-catalog.md에 있는 번호만 쓰세요.';
  return [
    'SIMPLE KOREAN 스킬이 자동으로 켜졌습니다',
    '',
    `사용자가 스킬 이름을 말하지 않아도 아래 글쓰기 규칙을 따르세요. 엄격 모드나 점검을 요청받거나 적용한 규칙의 번호를 적어야 하면 ${where}`,
    '',
  ].join('\n');
}

function candidates(pluginRoot, hookDirectory, relative) {
  const roots = [];
  if (pluginRoot) {
    roots.push(pluginRoot);
  }
  roots.push(path.join(hookDirectory, '..', '..'), path.join(hookDirectory, '..'));
  return roots.map((root) => path.join(root, ...relative));
}

function promptCandidates(pluginRoot, hookDirectory) {
  return candidates(pluginRoot, hookDirectory, ['prompts', 'system-prompt.md']);
}

function skillPath(pluginRoot, hookDirectory) {
  const found = candidates(pluginRoot, hookDirectory, ['skills', 'simple-korean', 'SKILL.md'])
    .find((candidate) => fs.existsSync(candidate));
  return found ? path.resolve(found) : '';
}

function readFirstFile(list) {
  for (const candidate of list) {
    try {
      return fs.readFileSync(candidate, 'utf8');
    } catch (error) {
      // 없거나, 읽을 수 없거나, 디렉터리다. 다음 후보를 읽는다.
    }
  }
  return '';
}

function stripFrontmatter(content) {
  return content.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, '');
}

// prompts/system-prompt.md는 사람이 읽는 페이지다. 제목, 붙여 넣는 곳을 알리는 문단, 두 "---" 줄
// 사이의 규칙 블록, 짧은 판본으로 이루어진다. 모델에는 규칙 블록만 보낸다.
function ruleBlock(content) {
  const fence = /^---[ \t]*\r?$/m;
  const first = content.search(fence);
  if (first === -1) {
    return content;
  }
  const rest = content.slice(first).replace(fence, '');
  const second = rest.search(fence);
  return second === -1 ? rest : rest.slice(0, second);
}

function buildContext(promptText, skill = '') {
  if (!promptText) {
    return FALLBACK_CONTEXT;
  }
  const out = header(skill) + ruleBlock(stripFrontmatter(promptText)).trim();
  if (out.length > MAX_CHARS) {
    process.stderr.write(`simple-korean 훅: 규칙이 ${out.length}자로 상한 ${MAX_CHARS}자를 넘어 짧은 대체 규칙을 보냅니다\n`);
    return FALLBACK_CONTEXT;
  }
  return out;
}

function main() {
  const pluginRoot = process.env.PLUGIN_ROOT || process.env.CLAUDE_PLUGIN_ROOT;
  const prompt = readFirstFile(promptCandidates(pluginRoot, __dirname));
  process.stdout.write(buildContext(prompt, skillPath(pluginRoot, __dirname)));
}

if (require.main === module) {
  main();
}

module.exports = {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  promptCandidates,
  readFirstFile,
  ruleBlock,
  skillPath,
  stripFrontmatter,
};
