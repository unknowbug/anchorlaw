/**
 * audit_preset_rows.mjs — preset 行解析性门禁（fail-closed）
 *
 * 用途：校验 agent preset composition 里每一行的 `name:` 能否在当前 harness 版本中解析。
 *       上游改名/移除插件包时本脚本非零退出，避免等用户 resume 会话时才看到
 *       `failed to mount`（2026-09-09 上游漂移事故：dsh-workflow-worker-thread 改名
 *       dsh-workflow-ptc，见 .investigations/dsh-upstream-drift-20260909/报告.md）。
 *
 * 用法：
 *   node dsh/tests/audit_preset_rows.mjs                          # 默认：源码 composition + 已安装副本（若存在）
 *   node dsh/tests/audit_preset_rows.mjs <composition.yml ...>    # 指定源码 composition（跳过 ./ 本地行）
 *   node dsh/tests/audit_preset_rows.mjs --installed <preset ...> # 校验 ~/.dsh/.agent-presets/<名>/agent.cordis.yml
 *   node dsh/tests/audit_preset_rows.mjs --harness-base <dir>     # 显式指定包名解析基准
 *
 * 环境：
 *   DSH_CHECKOUT     harness 源码 checkout（默认 D:\git\deepseek-harness）
 *   DSH_HARNESS_BASE 已安装 harness 所在目录（包名解析基准；通常无需设置，见下）
 *   DSH_HOME         默认 %USERPROFILE%\.dsh
 *
 * 判据（镜像上游 `classifyRowSpecifier()` + `packageInstalled()` 的最新语义）：
 *   - `cordis:` 前缀   → 内置行，放行
 *   - 以 `.` 开头       → preset 自带文件，相对 composition 所在目录解析；
 *                        源码树跳过（install.ps1 拷贝后才成立），已安装副本要求文件存在
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

const HARNESS = process.env.DSH_CHECKOUT ?? 'D:\\git\\deepseek-harness'
const HOME = process.env.DSH_HOME ?? join(process.env.USERPROFILE ?? '', '.dsh')

const args = process.argv.slice(2)
const installedMode = args.includes('--installed')

/** `--harness-base <dir>`（也接受 `--harness-base=<dir>`）。 */
function argValue(flag) {
  const eq = args.find(a => a.startsWith(`${flag}=`))
  if (eq !== undefined) return eq.slice(flag.length + 1)
  const at = args.indexOf(flag)
  return at >= 0 && at + 1 < args.length ? args[at + 1] : undefined
}

const harnessBaseArg = argValue('--harness-base')

/** Positional composition paths — every flag AND a flag's separate value removed. */
const positional = []
for (let i = 0; i < args.length; i++) {
  const a = args[i]
  if (a === '--installed') continue
  if (a === '--harness-base') { i++; continue }        // skip the flag and its value
  if (a.startsWith('--')) continue
  positional.push(a)
}

/** 目标文件：[{ file, sourceTree }] */
let files
if (installedMode) {
  files = positional.map(name => ({
    file: join(HOME, '.agent-presets', name, 'agent.cordis.yml'),
    sourceTree: false,
  }))
} else if (positional.length > 0) {
  files = positional.map(f => ({ file: f, sourceTree: true }))
} else {
  // selfcheck 默认：源码 composition（跳过 ./ 本地行）+ 已安装副本（若存在）
  files = [{ file: join(REPO, 'dsh', 'preset', 'agent.cordis.yml'), sourceTree: true }]
  const installed = join(HOME, '.agent-presets', 'anchorlaw', 'agent.cordis.yml')
  if (existsSync(installed)) files.push({ file: installed, sourceTree: false })
}

// ── 解析器（harness 的 entryListSchema + 其 js-yaml）；缺失则跳过并显式说明 ──
const schemaEntry = join(HARNESS, 'vendor', 'include', 'lib', 'index.js')
const yamlCandidates = [
  join(HARNESS, 'node_modules', '.pnpm', 'js-yaml@4.2.0', 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'),
  join(HARNESS, 'node_modules', 'js-yaml', 'dist', 'js-yaml.mjs'),
]

if (!existsSync(schemaEntry)) {
  console.log(`SKIP: harness checkout not found at ${HARNESS} (set DSH_CHECKOUT) — cannot resolve packages`)
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
  const pkgs = join(HARNESS, 'packages')
  if (existsSync(pkgs)) {
    for (const g of readdirSync(pkgs, { withFileTypes: true })) {
      if (g.isDirectory()) roots.push(join(pkgs, g.name))
    }
  }
  roots.push(join(HARNESS, 'vendor'), join(HARNESS, 'apps'))
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

/** composition 里全部行的 name（含嵌套 group） */
function rowNames(file) {
  const rows = yaml.load(readFileSync(file, 'utf8'), { schema: include.entryListSchema })
  const out = []
  const walk = list => {
    for (const row of list) {
      if (typeof row?.name === 'string') out.push(row.name)
      if (Array.isArray(row?.config)) walk(row.config)
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
    // A preset's own files travel with it: after install.ps1 copies preset/ into
    // ~/.dsh/.agent-presets/<id>/, the relative path resolves inside the preset
    // directory. In the source tree the copy has not happened yet.
    if (sourceTree) return { kind: 'preset', ok: true, why: 'preset-relative path (source tree — travels on install)' }
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
