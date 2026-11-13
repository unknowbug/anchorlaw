/**
 * audit_preset_rows.mjs — preset 行解析性门禁（fail-closed）
 *
 * 用途：校验 agent preset composition 里每一行的 `name:` 能否在当前 harness 版本中解析。
 *       上游改名/移除插件包时本脚本非零退出，避免等用户 resume 会话时才看到
 *       `failed to mount`（2026-09-09 上游漂移事故：dsh-workflow-worker-thread 改名
 *       dsh-workflow-ptc）。
 *
 * 用法：
 *   node dsh/tests/audit_preset_rows.mjs                        # 默认：本仓库 bundle patch（dsh/cordis.patch.yml）
 *   node dsh/tests/audit_preset_rows.mjs <file.yml ...>         # 指定文件（bundle patch 或旧 entry list）
 *   node dsh/tests/audit_preset_rows.mjs --harness-base <dir>   # 显式指定包名解析基准
 *
 * 环境：
 *   DSH_CHECKOUT     harness 源码 checkout（默认 D:\git\deepseek-harness）
 *   DSH_HARNESS_BASE 已安装 harness 所在目录（包名解析基准；通常无需设置，见下）
 *
 * 判据（镜像上游 `classifyRowSpecifier()` + `packageInstalled()` 的最新语义）：
 *   - `cordis:` 前缀   → 内置行，放行
 *   - 以 `.` 开头       → bundle 自带文件，锚定在**该 patch 文件所在目录**（上游
 *                        `anchorInsertedPluginNames()` 语义；仅顶层 insert 生效，
 *                        `config.plugins[]` 内的相对路径不会被锚定）
 *   - `file:` / 绝对路径 → 文件 URL，要求文件存在（Windows 盘符路径必须走 file URL）
 *   - 其余             → 包名，从 **已安装 harness 基准**（harness base）向上走
 *                        node_modules 查找（上游同款）；命中后再用 workspace manifest
 *                        校验子路径是否在 exports 内（比上游健康检查更严，因 exports
 *                        外的子路径在挂载时会真的 import 失败）
 *
 * 包名解析基准（harness base）——上游语义 + 本脚本的探测与守卫：
 *   上游 `mount.ts` 明确规定：本地 preset 位于用户 home 下，Node 向上 node_modules
 *   查找永远走不到 harness 依赖，故包名从"已安装 harness 所在目录"解析而非 preset 目录。
 *   该目录随部署形态而变，所以本脚本**自动探测**：按 `--harness-base` / `DSH_HARNESS_BASE`
 *   / `<checkout>/apps/cli` / `<checkout>` / `<checkout>/packages/bundle/base` 顺序取第一个
 *   能解析探针包（`@deepseek-ai/dsh-persona`）的候选。
 *
 *   **错基准守卫**：基准一旦选错（例如误传 checkout 根），会表现为"所有包行一起失败"，
 *   而真实的上游改名只失败个别行。因此包行**全数失败且数量 ≥ 2** 时本脚本判定基准可疑，
 *   输出 SKIP（exit 2）+ 诊断，而不是把 BAD 刷满屏——门禁误报会教人不信任门禁，
 *   比漏报更伤（2026-09-15 实测：传 checkout 根会让 shipped 与用户 preset 全量误报 BROKEN）。
 *
 * 退出码：0 = 全部可解析；1 = 存在不可解析行（真实漂移）；2 = 无法判定（缺解析器 / 基准可疑）
 *
 * 注：composition 使用 `!!js` 标签，必须用 harness 的 entryListSchema 解析，
 *     普通 js-yaml 会报 unknown tag（属正常，非缺陷）。
 */
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { join, dirname, resolve, isAbsolute } from 'node:path'
import { pathToFileURL, fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const REPO = resolve(HERE, '..', '..')

/**
 * harness 布局：源码 checkout（有 `packages/`）或已安装的 asar 运行时。
 *
 * Desktop 把整个运行时打进 `resources/app.asar`，**普通 Node 的 fs 读不到 asar**——
 * 这种布局必须用 `ELECTRON_RUN_AS_NODE=1 "<app>.exe"` 来跑本脚本（Electron 的 fs
 * 透明读 asar）。两种布局的包都落在 `<HARNESS>/node_modules`，所以包名解析与
 * exports 校验的代码不变。
 */
const CHECKOUT = process.env.DSH_CHECKOUT ?? 'D:\\git\\deepseek-harness'

/** 已安装 harness 的 `resources` 目录（含 `app.asar`）；找不到返回 undefined。 */
function detectInstallDir() {
  const roots = [
    process.env.DSH_INSTALL_DIR,
    process.env.ProgramFiles ? join(process.env.ProgramFiles, 'DeepSeek Harness', 'resources') : undefined,
    process.env.LOCALAPPDATA ? join(process.env.LOCALAPPDATA, 'Programs', 'DeepSeek Harness', 'resources') : undefined,
  ].filter(root => typeof root === 'string' && root !== '')
  return roots.find(root => existsSync(join(root, 'app.asar')))
}

const INSTALL_DIR = detectInstallDir()
const ASAR_DSH = INSTALL_DIR === undefined ? undefined : join(INSTALL_DIR, 'app.asar', 'dsh')

/** 选布局：源码 checkout 优先（开发机），否则已安装的 asar 运行时。 */
const LAYOUT = existsSync(join(CHECKOUT, 'packages')) ? 'checkout'
  : ASAR_DSH !== undefined && existsSync(join(ASAR_DSH, 'node_modules')) ? 'asar'
    : 'checkout'

const HARNESS = LAYOUT === 'asar' ? ASAR_DSH : CHECKOUT
const args = process.argv.slice(2)

/** `--harness-base <dir>`（也接受 `--harness-base=<dir>`）。 */
function argValue(flag) {
  const eq = args.find(a => a.startsWith(`${flag}=`))
  if (eq !== undefined) return eq.slice(flag.length + 1)
  const at = args.indexOf(flag)
  return at >= 0 && at + 1 < args.length ? args[at + 1] : undefined
}

const harnessBaseArg = argValue('--harness-base')

/** Positional 文件路径 — 每个 flag 及其独立取值都剔除。 */
const positional = []
for (let i = 0; i < args.length; i++) {
  const a = args[i]
  if (a === '--harness-base') { i++; continue }        // skip the flag and its value
  if (a.startsWith('--')) continue
  positional.push(a)
}

/** 目标文件：[{ file, sourceTree }] */
let files
if (positional.length > 0) {
  files = positional.map(f => ({ file: f, sourceTree: true }))
} else {
  // selfcheck 默认：bundle patch（DSH >= 0.1.7 的 preset 载体）。
  // 主目标缺失 = 门禁失效，必须报错而不是静默跳过——本门禁存在的理由就是
  // "别让会话在运行时才发现 preset 挂不上"。
  const patch = join(REPO, 'dsh', 'cordis.patch.yml')
  if (!existsSync(patch)) {
    console.log(`FAIL: bundle patch not found at ${patch} — nothing to verify`)
    process.exit(1)
  }
  files = [{ file: patch, sourceTree: false }]
}

// ── 解析器（harness 的 entryListSchema + 其 js-yaml）；缺失则跳过并显式说明 ──
// checkout：include 构建产物在 vendor/；已安装布局：它就是一个普通依赖包。
const schemaEntry = (LAYOUT === 'asar'
  ? [join(HARNESS, 'node_modules', '@deepseek-ai', 'cordis-plugin-include', 'lib', 'index.js')]
  : [join(HARNESS, 'vendor', 'include', 'lib', 'index.js')]
).find(existsSync)
const yamlCandidates = [
  join(HARNESS, 'node_modules', '.pnpm', 'js-yaml@4.2.0', 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'),
  join(HARNESS, 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'),
]

if (schemaEntry === undefined) {
  console.log(`SKIP: cannot read the harness at ${HARNESS} (layout: ${LAYOUT}) — cannot resolve packages`)
  if (LAYOUT === 'checkout' && INSTALL_DIR !== undefined) {
    console.log('      this install is packed in app.asar, which plain Node cannot read:')
    console.log(`      run this gate with ELECTRON_RUN_AS_NODE=1 "${join(INSTALL_DIR, '..', 'DeepSeek Harness.exe')}"`)
  } else if (LAYOUT === 'checkout') {
    console.log('      set DSH_CHECKOUT to a harness source checkout')
  }
  process.exit(2)
}
const yamlPath = yamlCandidates.find(existsSync)
if (!yamlPath) {
  console.log(`SKIP: js-yaml not found under ${HARNESS} — cannot parse composition`)
  process.exit(2)
}

const include = await import(pathToFileURL(schemaEntry).href)
const yaml = await import(pathToFileURL(yamlPath).href)

/**
 * Mirror of upstream `packageInstalled()` (agent-presets `src/discovery.ts`):
 * walk up from a base looking for `node_modules/<pkg>/package.json`.
 * Deliberately tolerant of unexported subpaths, exactly like upstream's health
 * check — the stricter `exports` probe is applied separately, below.
 */
function packageInstalled(name, base) {
  const pkg = name.split('/').slice(0, name.startsWith('@') ? 2 : 1).join('/')
  let dir = base
  for (;;) {
    if (existsSync(join(dir, 'node_modules', pkg, 'package.json'))) return true
    const parent = dirname(dir)
    if (parent === dir) return false
    dir = parent
  }
}

// ── 包名解析基准：自动探测（上游语义：包名从"已安装 harness 所在处"解析）──────
// 探针包取每个 host preset 都必然含有的 @deepseek-ai/dsh-persona：能解析它，
// 说明该候选确实是 harness 的依赖根。
const PROBE_PACKAGE = '@deepseek-ai/dsh-persona'
const baseCandidates = [
  harnessBaseArg,
  process.env.DSH_HARNESS_BASE,
  join(HARNESS, 'apps', 'cli'),
  HARNESS,
  join(HARNESS, 'packages', 'bundle', 'base'),
].filter(c => typeof c === 'string' && c !== '')

const triedBases = []
let HARNESS_BASE = null
for (const candidate of baseCandidates) {
  triedBases.push(candidate)
  if (packageInstalled(PROBE_PACKAGE, candidate)) { HARNESS_BASE = candidate; break }
}

if (HARNESS_BASE === null) {
  console.log(`SKIP: no harness base resolves ${PROBE_PACKAGE} — cannot judge package rows`)
  for (const c of triedBases) console.log(`   tried: ${c}`)
  console.log('   hint: pass --harness-base <installed harness dir>, or set DSH_HARNESS_BASE')
  process.exit(2)
}

/** 收集 harness workspace 里所有包：name -> { dir, exports }（用于 exports 子路径严格校验） */
function collectPackages() {
  const map = new Map()
  const roots = []
  if (LAYOUT === 'asar') {
    // 已安装布局：@deepseek-ai/<pkg> 直接挂在 node_modules 下（没有 workspace 的 packages/）。
    const scope = join(HARNESS, 'node_modules', '@deepseek-ai')
    if (existsSync(scope)) roots.push(scope)
  } else {
    const pkgs = join(HARNESS, 'packages')
    if (existsSync(pkgs)) {
      for (const g of readdirSync(pkgs, { withFileTypes: true })) {
        if (g.isDirectory()) roots.push(join(pkgs, g.name))
      }
    }
    roots.push(join(HARNESS, 'vendor'), join(HARNESS, 'apps'))
  }
  for (const root of roots) {
    if (!existsSync(root)) continue
    for (const entry of readdirSync(root, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue
      const pj = join(root, entry.name, 'package.json')
      if (!existsSync(pj)) continue
      try {
        const manifest = JSON.parse(readFileSync(pj, 'utf8'))
        if (typeof manifest.name === 'string') {
          map.set(manifest.name, { dir: join(root, entry.name), exports: manifest.exports })
        }
      } catch { /* 坏 manifest 忽略 */ }
    }
  }
  return map
}

const packages = collectPackages()

/**
 * 本仓库自己的 bundle 清单（`dsh/package.json`）。bundle 的 preset 行用**裸包名**
 * 指向自身插件（`<name>/plugin`）——这个包不在 harness 里，也不在任何 node_modules
 * 中（由安装步骤以依赖形式进入 profile），所以不能走 harness base 查找，
 * 只能用本仓库清单的 `exports` 校验子路径。
 */
const SELF_BUNDLE = (() => {
  const p = join(REPO, 'dsh', 'package.json')
  if (!existsSync(p)) return undefined
  try {
    const m = JSON.parse(readFileSync(p, 'utf8'))
    return typeof m.name === 'string' ? m : undefined
  } catch {
    return undefined
  }
})()

/**
 * 全部行的 name。
 *
 * 必须覆盖两种载体 + 三条递归路径，缺一即漏检：
 *   载体 a. bundle patch（顶层是 `- insert: [...]`，DSH >= 0.1.7 的 preset 载体）
 *   载体 b. 旧 entry list（顶层直接是行数组，0.1.6 及更早）
 *   递归 1. `insert[]`            —— 载体 a 的行在这里
 *   递归 2. `config[]`（group 子行）
 *   递归 3. `config.plugins[]`    —— **preset 行的子行列表，新版机制的全部内容**
 *
 * 2026-09-23 事故：本函数原先只走递归 2，且不认识载体 a，于是上游 0.1.7 把 preset
 * 换成 bundle patch 后，本门禁**全绿**而 resume 报 `Unknown agent preset: anchorlaw`
 * （实测漏检 27/28 行）。递归 1/3 是那次事故的修复本体，勿删。
 */
function rowNames(file) {
  const rows = yaml.load(readFileSync(file, 'utf8'), { schema: include.entryListSchema })
  const out = []
  const walk = list => {
    for (const row of list ?? []) {
      if (Array.isArray(row?.insert)) walk(row.insert)                    // 载体 a
      if (typeof row?.name === 'string') out.push(row.name)
      if (Array.isArray(row?.config)) walk(row.config)                    // group 子行
      if (Array.isArray(row?.config?.plugins)) walk(row.config.plugins)   // preset 子行
    }
  }
  walk(rows)
  return out
}

/**
 * Mirror of upstream `classifyRowSpecifier()` (agent-presets `src/specifier.ts`).
 *
 * The Loader splits every row specifier four ways, and only `kind` decides which
 * base it resolves against: `cordis:` builtins resolve nothing; a leading `.`
 * row ships its file with the preset (preset-relative); `file:` and absolute
 * paths become file URLs (needed for drive-letter paths on Windows); everything
 * else is a package name resolved from the harness base.
 */
function classifyRowSpecifier(name) {
  if (name.startsWith('cordis:')) return { kind: 'builtin', specifier: name }
  if (name.startsWith('.')) return { kind: 'preset', specifier: name }
  if (name.startsWith('file:')) return { kind: 'file', specifier: name }
  if (isAbsolute(name)) return { kind: 'file', specifier: pathToFileURL(name).href }
  return { kind: 'package', specifier: name }
}

/** 该结论是否属于"包在基准下找不到"（错基准与上游改名都表现为此） */
const PACKAGE_MISSING = 'package not installed above harness base'

/** 单个 name 的解析结论 */
function classify(name, presetDir, sourceTree) {
  const row = classifyRowSpecifier(name)
  if (row.kind === 'builtin') return { kind: 'builtin', ok: true, why: 'cordis builtin' }
  if (row.kind === 'preset') {
    // A bundle's own files travel with it: the patch anchors a relative row beside
    // the patch file (upstream `anchorInsertedPluginNames()`), so the target must
    // exist next to this file. The preset row's own subtree does NOT get this
    // anchoring — that is why rows inside `config.plugins[]` must be bare names.
    if (sourceTree) return { kind: 'preset', ok: true, why: 'patch-relative path (source tree — travels on install)' }
    const target = resolve(presetDir, row.specifier)
    return {
      kind: 'preset',
      ok: existsSync(target),
      why: existsSync(target) ? 'preset-relative file' : `preset file missing: ${target}`,
    }
  }
  if (row.kind === 'file') {
    const target = fileURLToPath(new URL(row.specifier))
    return {
      kind: 'file',
      ok: existsSync(target),
      why: existsSync(target) ? 'file row' : `file row missing: ${target}`,
    }
  }
  // 自引用：bundle 自身的包（preset 里的本地插件行）。它由安装步骤装进 profile，
  // 因此按设计就不在 harness base 下——用本仓库 bundle 清单的 exports 校验子路径，
  // 而不是误报"上游改名/移除"。
  const selfBase = row.specifier.startsWith('@')
    ? row.specifier.split('/').slice(0, 2).join('/')
    : row.specifier.split('/')[0]
  if (SELF_BUNDLE !== undefined && selfBase === SELF_BUNDLE.name) {
    const selfSub = row.specifier.slice(selfBase.length).replace(/^\//, '')
    const keys = Object.keys(SELF_BUNDLE.exports ?? {})
    if (selfSub !== '' && !keys.includes(`./${selfSub}`)) {
      return { kind: 'package', ok: false, why: `self-bundle subpath ./${selfSub} not in exports (have: ${keys.join(', ') || 'none'})` }
    }
    // exports 里有这个键还不够：**它指向的文件必须存在**。只校验键会让"插件文件被
    // 改名/移动"这种改动照样绿——与 2026-09-23 事故同一失效类（门禁绿、运行时挂载失败）。
    if (selfSub !== '') {
      const entry = SELF_BUNDLE.exports[`./${selfSub}`]
      const rel = typeof entry === 'string' ? entry : entry?.default
      if (typeof rel !== 'string') {
        return { kind: 'package', ok: false, why: `self-bundle export ./${selfSub} has no string target` }
      }
      if (!existsSync(join(REPO, 'dsh', rel))) {
        return { kind: 'package', ok: false, why: `self-bundle export ./${selfSub} points at a missing file: dsh/${rel}` }
      }
    }
    return { kind: 'package', ok: true, why: `self bundle (${SELF_BUNDLE.name})` }
  }
  // Package row — upstream's rule is the upward node_modules walk from the
  // harness base. A package absent there cannot be imported at mount time.
  if (!packageInstalled(row.specifier, HARNESS_BASE)) {
    return {
      kind: 'package',
      ok: false,
      missing: true,
      why: `${PACKAGE_MISSING} ${HARNESS_BASE} (renamed / removed upstream)`,
    }
  }
  // Extra strictness beyond upstream's health check (which accepts unexported
  // subpaths): a subpath outside the package's `exports` map still fails the
  // ESM import at mount time, so flag it when the workspace manifest is known.
  const isScoped = row.specifier.startsWith('@')
  const seg = row.specifier.split('/')
  const base = isScoped ? seg.slice(0, 2).join('/') : seg[0]
  const sub = isScoped ? seg.slice(2).join('/') : seg.slice(1).join('/')
  const manifest = packages.get(base)
  if (sub !== '' && manifest && (!manifest.exports || !Object.keys(manifest.exports).includes(`./${sub}`))) {
    const keys = manifest.exports ? Object.keys(manifest.exports).join(', ') : 'none'
    return { kind: 'package', ok: false, why: `subpath ./${sub} not in ${base} exports (have: ${keys})` }
  }
  return { kind: 'package', ok: true, why: `package (harness base: ${HARNESS_BASE})` }
}

const results = []
let bad = 0
let packageRows = 0
let packageMissing = 0

for (const { file, sourceTree } of files) {
  console.log(`\n== ${file}${sourceTree ? '  (source tree)' : '  (installed)'}`)
  if (!existsSync(file)) {
    console.log('   (file not present — skipped)')
    continue
  }
  let names
  try {
    names = [...new Set(rowNames(file))]
  } catch (e) {
    console.log(`   PARSE FAIL: ${e.message}`)
    bad++
    continue
  }
  let fileBad = 0
  for (const name of names.sort()) {
    const r = classify(name, dirname(file), sourceTree)
    if (r.kind === 'package') { packageRows++; if (r.missing) packageMissing++ }
    if (!r.ok) { fileBad++; bad++ }
    console.log(`   ${r.ok ? 'OK  ' : 'BAD '} ${name}${r.ok ? '' : `  <- ${r.why}`}`)
    results.push({ name, r })
  }
  console.log(`   -> ${names.length} reference(s), ${fileBad} unresolvable`)
}

// ── 错基准守卫：包行"全数"失败 = 基准可疑，而非上游改名（改名只影响个别行）──
// 误报会让维护者去"修"本来正确的 preset，比漏报更伤，故此处降级为 SKIP + 诊断。
if (packageRows >= 2 && packageMissing === packageRows) {
  console.log(`\nSKIP: all ${packageRows} package row(s) failed to resolve — the harness base looks wrong,`)
  console.log(`      not a rename (a real rename fails one or a few rows).`)
  console.log(`      base in use: ${HARNESS_BASE}`)
  for (const c of triedBases) console.log(`      tried: ${c}`)
  console.log('      hint: pass --harness-base <installed harness dir>, or set DSH_HARNESS_BASE')
  process.exit(2)
}

console.log(bad === 0 ? '\nAll preset rows resolvable ✅' : `\n${bad} unresolvable preset row(s) ❌`)
process.exit(bad === 0 ? 0 : 1)
