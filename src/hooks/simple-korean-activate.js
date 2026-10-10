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

const CONFIG_NAME = '.simple-korean.json';
// 설정 값은 저장소가 정하고, 이 훅을 거쳐 모델의 문맥에 들어간다. 그래서 evals/ko_terms.py의
// load_config, form_ok와 같은 기준으로 검사하고, 단어 목록에 있는 개념 id와 한 줄짜리 짧은 지정형만 적는다.
const CONFIG_KEYS = new Set(['terms', 'skip', 'spacing']);
const MAX_FORM_CHARS = 20;
const MAX_SKIP_ENTRIES = 100;
const FORM_CHARS = /^[가-힣A-Za-z0-9 ]+$/u;
const ID_PATTERN = /^[a-z0-9_]{1,40}$/;
const NOT_PRINTABLE = /(?! )[\p{C}\p{Z}]/u;

// 경로처럼 밖에서 온 글을 한 줄로 만든다. 줄바꿈과 제어 문자는 \u 꼴로 바꾸고 limit자에서 자른다.
function oneLine(text, limit = 200) {
  const flat = String(text).replace(/[\p{C}\p{Zl}\p{Zp}]/gu,
    (ch) => `\\u${ch.codePointAt(0).toString(16).padStart(4, '0')}`);
  return flat.length <= limit ? flat : `${flat.slice(0, limit)}…`;
}

// 지정형은 NFC로 맞춘 뒤 한글, 영문, 숫자, 공백만 받는다. 단어 목록의 형태는 모두 한글과 공백이다.
function formOk(form) {
  const normalized = form.normalize('NFC');
  const length = [...normalized.replace(/^ +| +$/g, '')].length;
  return FORM_CHARS.test(normalized) && length > 0 && length <= MAX_FORM_CHARS;
}

function skipOk(skip) {
  return Array.isArray(skip) && skip.length <= MAX_SKIP_ENTRIES
    && skip.every((item) => typeof item === 'string' && !NOT_PRINTABLE.test(item) && item.replace(/^ +| +$/g, '') !== '');
}

function isObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function entryOk(value) {
  const entry = typeof value === 'string' ? { write: value } : value;
  return isObject(entry)
    && Object.keys(entry).every((key) => key === 'write' || key === 'reason')
    && typeof entry.write === 'string' && formOk(entry.write)
    && (entry.reason === undefined || typeof entry.reason === 'string');
}

function validConfig(config) {
  if (!isObject(config) || Object.keys(config).some((key) => !CONFIG_KEYS.has(key))) {
    return false;
  }
  const { terms = {}, skip = [], spacing = 'attached' } = config;
  return (spacing === 'attached' || spacing === 'spaced')
    && isObject(terms) && Object.values(terms).every(entryOk) && skipOk(skip);
}

// 단어 목록(data/terms.json)의 개념 id. 목록을 읽지 못하면 null이고, 그때는 ID_PATTERN에 맞는 id만 받는다.
function conceptIds(pluginRoot, hookDirectory) {
  try {
    const terms = JSON.parse(readFirstFile(candidates(pluginRoot, hookDirectory, ['data', 'terms.json'])));
    return new Set(terms.concepts.map((concept) => concept.id));
  } catch (error) {
    return null;
  }
}

// 작업 디렉터리에서 위로 올라가며 프로젝트 설정을 찾는다(evals/ko_terms.py의 find_config와 같다).
function findConfig(start) {
  let dir = path.resolve(start || '.');
  for (;;) {
    const candidate = path.join(dir, CONFIG_NAME);
    try {
      if (fs.statSync(candidate).isFile()) {
        return candidate;
      }
    } catch (error) {
      // 없다. 한 단계 위를 본다.
    }
    const parent = path.dirname(dir);
    if (parent === dir) {
      return '';
    }
    dir = parent;
  }
}

// 모델은 설정 파일을 스스로 읽지 않는다. 바뀐 지정형을 문맥에 직접 적어 준다. 형식이 틀린 설정은
// 린터처럼 통째로 무시하고, 단어 목록에 없는 개념은 적지 않는다.
function configNote(configPath, knownIds = conceptIds(process.env.PLUGIN_ROOT || process.env.CLAUDE_PLUGIN_ROOT, __dirname)) {
  if (!configPath) {
    return '';
  }
  let config;
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (error) {
    return `${oneLine(configPath)}을 읽지 못했습니다. 위 지정형을 쓰세요.`;
  }
  if (!validConfig(config)) {
    return `${oneLine(configPath)}의 형식이 틀려 무시했습니다. 위 지정형을 쓰세요.`;
  }
  const known = (id) => (knownIds ? knownIds.has(id) : ID_PATTERN.test(id));
  const pairs = Object.entries(config.terms || {})
    .filter(([id]) => known(id))
    .map(([id, value]) => [id, (typeof value === 'string' ? value : value.write).normalize('NFC')]);
  const parts = [];
  if (pairs.length) {
    parts.push(`이 레포지토리의 ${CONFIG_NAME}이 지정형을 바꿨습니다. 위 목록보다 이 형태를 먼저 쓰세요: ${pairs.map(([id, write]) => `${id} → ${write}`).join(', ')}.`);
  }
  if (config.spacing === 'spaced') {
    parts.push('이 레포지토리는 전문 용어 합성어를 띄어 쓰세요(매개 변수, 반환 값, 기본 값, 오픈 소스).');
  }
  return parts.join(' ');
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

function buildContext(promptText, skill = '', note = '') {
  if (!promptText) {
    return FALLBACK_CONTEXT;
  }
  const out = header(skill) + ruleBlock(stripFrontmatter(promptText)).trim() + (note ? `\n\n${note}` : '');
  if (out.length > MAX_CHARS) {
    process.stderr.write(`simple-korean 훅: 규칙이 ${out.length}자로 상한 ${MAX_CHARS}자를 넘어 짧은 대체 규칙을 보냅니다\n`);
    return FALLBACK_CONTEXT;
  }
  return out;
}

function main() {
  const pluginRoot = process.env.PLUGIN_ROOT || process.env.CLAUDE_PLUGIN_ROOT;
  const prompt = readFirstFile(promptCandidates(pluginRoot, __dirname));
  const note = configNote(findConfig(process.env.CLAUDE_PROJECT_DIR || process.cwd()));
  process.stdout.write(buildContext(prompt, skillPath(pluginRoot, __dirname), note));
}

if (require.main === module) {
  main();
}

module.exports = {
  FALLBACK_CONTEXT,
  MAX_CHARS,
  buildContext,
  configNote,
  findConfig,
  promptCandidates,
  readFirstFile,
  ruleBlock,
  skillPath,
  stripFrontmatter,
};
