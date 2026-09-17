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
 *
 * 环境：
 *   DSH_CHECKOUT     harness 源码 checkout（默认 D:\git\deepseek-harness）
 *   DSH_HARNESS_BASE 已安装 harness 所在目录（包名解析基准；默认 <DSH_CHECKOUT>\apps\cli）
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
 * 说明：包名解析基准是 harness base 而非 preset 目录——上游明确规定，
 *       本地 preset 位于用户 home 下，Node 向上查找永远走不到 harness 依赖。
 *
 * 退出码：0 = 全部可解析；1 = 存在不可解析行；2 = 无法执行（缺 harness checkout / 解析器）
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
// Where the INSTALLED harness lives: upstream resolves bare package names from
// this base (agent-presets `mount.ts`: a locally authored preset sits under the
// user's home, where Node's upward node_modules walk never reaches the harness's
// own dependencies). In a checkout that is apps/cli.
const HARNESS_BASE = process.env.DSH_HARNESS_BASE ?? join(HARNESS, 'apps', 'cli')
const HOME = process.env.DSH_HOME ?? join(process.env.USERPROFILE ?? '', '.dsh')

const args = process.argv.slice(2)
const installedMode = args.includes('--installed')
const positional = args.filter(a => !a.startsWith('--'))

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

/** 收集 harness workspace 里所有包：name -> { dir, exports } */
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

/**
 * Mirror of upstream `packageInstalled()` (agent-presets `src/discovery.ts`):
 * walk up from the harness base looking for `node_modules/<pkg>/package.json`.
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

/** 单个 name 的解析结论 */
function classify(name, presetDir, sourceTree) {
  const row = classifyRowSpecifier(name)
  if (row.kind === 'builtin') return { ok: true, why: 'cordis builtin' }
  if (row.kind === 'preset') {
    // A preset's own files travel with it: after install.ps1 copies preset/ into
    // ~/.dsh/.agent-presets/<id>/, the relative path resolves inside the preset
    // directory. In the source tree the copy has not happened yet.
    if (sourceTree) return { ok: true, why: 'preset-relative path (source tree — travels on install)' }
    const target = resolve(presetDir, row.specifier)
    return existsSync(target) ? { ok: true, why: 'preset-relative file' } : { ok: false, why: `preset file missing: ${target}` }
  }
  if (row.kind === 'file') {
    const target = fileURLToPath(new URL(row.specifier))
    return existsSync(target) ? { ok: true, why: 'file row' } : { ok: false, why: `file row missing: ${target}` }
  }
  // Package row — upstream's rule is the upward node_modules walk from the
  // harness base. A package absent there cannot be imported at mount time.
  if (!packageInstalled(row.specifier, HARNESS_BASE)) {
    return { ok: false, why: `package not installed above harness base ${HARNESS_BASE} (renamed / removed upstream)` }
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
    return { ok: false, why: `subpath ./${sub} not in ${base} exports (have: ${keys})` }
  }
  return { ok: true, why: `package (harness base: ${HARNESS_BASE})` }
}

let bad = 0
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
    if (!r.ok) { fileBad++; bad++ }
    console.log(`   ${r.ok ? 'OK  ' : 'BAD '} ${name}${r.ok ? '' : `  <- ${r.why}`}`)
  }
  console.log(`   -> ${names.length} reference(s), ${fileBad} unresolvable`)
}

console.log(bad === 0 ? '\nAll preset rows resolvable ✅' : `\n${bad} unresolvable preset row(s) ❌`)
process.exit(bad === 0 ? 0 : 1)
