/**
 * Defensive pattern scanner for TypeScript/JavaScript.
 *
 * Based on the Anchorlaw Protocol v0.1 — scanner pattern catalog.
 * Maturity: IN DEVELOPMENT — cross-language port of the verified Python scanner.
 */

import * as ts from "typescript";
import * as fs from "fs";
import * as path from "path";

// ---------------------------------------------------------------------------
// Data types
// ---------------------------------------------------------------------------

export enum PatternType {
  SWALLOWED_EXCEPTION = "swallowed-exception",
  BARE_EXCEPT = "bare-except",
  MISSING_ANCHOR = "missing-anchor",
  DEFENSIVE_NULL_CHAIN = "defensive-null-chain",
  VAGUE_TODO = "vague-todo",
  TRIVIAL_TEST = "trivial-test",
}

export interface DefensivePattern {
  patternType: PatternType;
  filePath: string;
  lineNumber: number;
  codeSnippet: string;
  suggestion: string;
  functionName: string;
}

const PATTERN_LABELS: Record<PatternType, string> = {
  [PatternType.SWALLOWED_EXCEPTION]: "swallowed-exception",
  [PatternType.BARE_EXCEPT]: "bare-except",
  [PatternType.MISSING_ANCHOR]: "missing-anchor",
  [PatternType.DEFENSIVE_NULL_CHAIN]: "defensive-null-chain",
  [PatternType.VAGUE_TODO]: "vague-todo",
  [PatternType.TRIVIAL_TEST]: "trivial-test",
};

const PATTERN_SEVERITY: Record<PatternType, string> = {
  [PatternType.SWALLOWED_EXCEPTION]: "error",
  [PatternType.BARE_EXCEPT]: "error",
  [PatternType.MISSING_ANCHOR]: "warning",
  [PatternType.DEFENSIVE_NULL_CHAIN]: "warning",
  [PatternType.VAGUE_TODO]: "info",
  [PatternType.TRIVIAL_TEST]: "warning",
};

const PATTERN_MESSAGES: Record<PatternType, string> = {
  [PatternType.SWALLOWED_EXCEPTION]:
    "Exception swallowed without handling. " +
    "Is this known to be safe (document why)? " +
    "Or do you not know how to handle it (use @anchor.i_dont_know)?",
  [PatternType.BARE_EXCEPT]:
    "Broad catch clause catches unknown errors. " +
    "You don't know what you're catching — this is a defensive programming signal. " +
    "Specify the exact error type.",
  [PatternType.MISSING_ANCHOR]:
    "Public function has no anchorlaw anchor " +
    "(@anchor.test or @anchor.i_dont_know). " +
    "On what basis does it claim correctness?",
  [PatternType.DEFENSIVE_NULL_CHAIN]:
    "Chained null checks returning null — you are propagating the problem " +
    "rather than solving it. Express non-nullability in the type system, " +
    "or handle the null boundary at the entry point.",
  [PatternType.VAGUE_TODO]:
    "TODO without issue tracker reference. " +
    "This is a 'I know there's a problem but won't commit to fixing it' defensive signal.",
  [PatternType.TRIVIAL_TEST]:
    "This test assertion may be tautological. " +
    "Test anchors must contain substantive practice validation.",
};

// ---------------------------------------------------------------------------
// Scanner
// ---------------------------------------------------------------------------

class Scanner {
  private fileName: string;
  private sourceLines: string[];
  private patterns: DefensivePattern[] = [];
  private currentFunction = "";
  private sourceFile: ts.SourceFile;

  constructor(filePath: string) {
    this.fileName = filePath;
    const source = fs.readFileSync(filePath, "utf-8");
    this.sourceLines = source.split("\n");
    this.sourceFile = ts.createSourceFile(
      filePath,
      source,
      ts.ScriptTarget.Latest,
      true,
    );
  }

  scan(): DefensivePattern[] {
    this.walk(this.sourceFile);

    // Comment-based checks
    this.scanComments();

    // Anchor check
    this.scanMissingAnchors();

    return this.patterns.sort((a, b) => a.lineNumber - b.lineNumber);
  }

  // ---- helpers ----

  private add(
    ptype: PatternType,
    node: ts.Node,
    suggestion?: string,
    functionName?: string,
  ): void {
    const { line } = this.sourceFile.getLineAndCharacterOfPosition(
      node.getStart(),
    );
    this.patterns.push({
      patternType: ptype,
      filePath: this.fileName,
      lineNumber: line + 1,
      codeSnippet: this.sourceLines[line]?.trim() || "",
      suggestion: suggestion || PATTERN_MESSAGES[ptype],
      functionName: functionName || this.currentFunction,
    });
  }

  // ---- AST walker ----

  private walk(node: ts.Node): void {
    switch (node.kind) {
      case ts.SyntaxKind.FunctionDeclaration:
      case ts.SyntaxKind.FunctionExpression:
      case ts.SyntaxKind.ArrowFunction:
      case ts.SyntaxKind.MethodDeclaration:
        this.checkFunction(node as ts.FunctionLikeDeclaration);
        break;

      case ts.SyntaxKind.TryStatement:
        this.checkTryStatement(node as ts.TryStatement);
        break;

      case ts.SyntaxKind.CallExpression:
        this.checkCallExpression(node as ts.CallExpression);
        break;
    }

    ts.forEachChild(node, (child) => this.walk(child));
  }

  // ---- individual checks ----

  private checkFunction(node: ts.FunctionLikeDeclaration): void {
    const body = node.body;
    if (!body) return;

    let nullReturnCount = 0;

    const countNullReturns = (n: ts.Node): void => {
      if (ts.isIfStatement(n)) {
        if (this.isNullCheckReturnNull(n)) {
          nullReturnCount++;
        }
      }
      ts.forEachChild(n, countNullReturns);
    };
    countNullReturns(body);

    if (nullReturnCount >= 3) {
      const name = node.name
        ? (node.name as ts.Identifier).text
        : "<anonymous>";
      this.add(
        PatternType.DEFENSIVE_NULL_CHAIN,
        node,
        `Function ${name} contains ${nullReturnCount} ` +
          "'if (x === null) return null' patterns. " +
          PATTERN_MESSAGES[PatternType.DEFENSIVE_NULL_CHAIN],
        name,
      );
    }
  }

  private checkTryStatement(node: ts.TryStatement): void {
    const catchClause = node.catchClause;
    if (!catchClause) return;

    // Check for broad catch: catch (e) or catch (e: any)
    const binding = catchClause.variableDeclaration;
    if (!binding || !binding.type) {
      // No type annotation = catches anything
      this.add(PatternType.BARE_EXCEPT, catchClause);
    } else if (
      ts.isTypeReferenceNode(binding.type) &&
      ts.isIdentifier(binding.type.typeName) &&
      binding.type.typeName.text === "any"
    ) {
      this.add(PatternType.BARE_EXCEPT, catchClause);
    }

    // Check for swallowed: empty block or just console.log
    const body = catchClause.block;
    const statements = body.statements;
    if (statements.length === 0) {
      this.add(PatternType.SWALLOWED_EXCEPTION, catchClause);
    } else if (statements.length === 1) {
      const stmt = statements[0];
      if (ts.isExpressionStatement(stmt)) {
        const expr = stmt.expression;
        if (ts.isCallExpression(expr)) {
          const callee = expr.expression;
          if (
            ts.isPropertyAccessExpression(callee) &&
            ts.isIdentifier(callee.expression) &&
            callee.expression.text === "console"
          ) {
            this.add(
              PatternType.SWALLOWED_EXCEPTION,
              catchClause,
              "Logging without handling — typically a defensive pattern.",
            );
          }
        }
      }
    }
  }

  private isNullCheckReturnNull(node: ts.IfStatement): boolean {
    if (!ts.isBinaryExpression(node.expression)) return false;
    const expr = node.expression;
    const isNullCheck =
      (expr.operatorToken.kind === ts.SyntaxKind.EqualsEqualsEqualsToken ||
        expr.operatorToken.kind === ts.SyntaxKind.EqualsEqualsToken) &&
      expr.right.kind === ts.SyntaxKind.NullKeyword;

    if (!isNullCheck) return false;

    // Check that the body statement is `return null` or `return`
    const thenStmt = node.thenStatement;
    if (ts.isBlock(thenStmt) && thenStmt.statements.length === 1) {
      const inner = thenStmt.statements[0];
      if (ts.isReturnStatement(inner)) {
        if (!inner.expression) return true;
        if (inner.expression.kind === ts.SyntaxKind.NullKeyword) return true;
      }
    }
    if (ts.isReturnStatement(thenStmt)) {
      if (!thenStmt.expression) return true;
      if (thenStmt.expression.kind === ts.SyntaxKind.NullKeyword) return true;
    }

    return false;
  }

  private checkCallExpression(node: ts.CallExpression): void {
    // Check for tautological expect(f(x)).toBe(f(x)) patterns
    const callee = node.expression;
    if (!ts.isPropertyAccessExpression(callee)) return;
    if (callee.name.text !== "toBe" && callee.name.text !== "toEqual") return;

    // Compare the expect argument with the toBe argument
    const expectCall = callee.expression;
    if (!ts.isCallExpression(expectCall)) return;
    if (!ts.isIdentifier(expectCall.expression)) return;
    if (expectCall.expression.text !== "expect") return;
    if (expectCall.arguments.length !== 1) return;

    const expectArg = expectCall.arguments[0];
    const toBeArg = node.arguments[0];

    // Simple check: same text representation
    if (
      expectArg.getText(this.sourceFile) === toBeArg.getText(this.sourceFile)
    ) {
      this.add(
        PatternType.TRIVIAL_TEST,
        node,
        "This assertion compares a value to itself — it is tautological.",
      );
    }
  }

  // ---- comment-based checks ----

  private scanComments(): void {
    const vagueTodoRegex = /\/\/\s*(TODO|FIXME|HACK|XXX)\s*:?\s*(?!.*\b(issues?|ticket|GH-|#)\d+).*$/i;

    this.sourceLines.forEach((line, i) => {
      if (vagueTodoRegex.test(line)) {
        this.patterns.push({
          patternType: PatternType.VAGUE_TODO,
          filePath: this.fileName,
          lineNumber: i + 1,
          codeSnippet: line.trim(),
          suggestion: PATTERN_MESSAGES[PatternType.VAGUE_TODO],
          functionName: "",
        });
      }
    });
  }

  // ---- missing anchor check ----

  private scanMissingAnchors(): void {
    const checkNode = (node: ts.Node): void => {
      if (
        ts.isFunctionDeclaration(node) ||
        ts.isMethodDeclaration(node)
      ) {
        const name = node.name
          ? (node.name as ts.Identifier).text
          : "";

        // Skip private (underscore-prefixed) and constructor
        if (name.startsWith("_") || name === "constructor") return;

        // Check modifiers for 'export' or no 'private' modifier
        const modifiers = ts.getModifiers(node);
        const isPrivate =
          modifiers?.some(
            (m) => m.kind === ts.SyntaxKind.PrivateKeyword,
          ) ?? false;
        if (isPrivate) return;

        // Check for @anchor.test or @anchor.i_dont_know in JSDoc
        const jsDoc = (node as any).jsDoc as
          | ts.JSDoc[]
          | undefined;
        let hasAnchor = false;
        if (jsDoc) {
          for (const doc of jsDoc) {
            if (doc.comment && typeof doc.comment === "string") {
              if (
                doc.comment.includes("@anchor.test") ||
                doc.comment.includes("@anchor.i_dont_know")
              ) {
                hasAnchor = true;
                break;
              }
            }
          }
        }

        if (!hasAnchor) {
          this.add(
            PatternType.MISSING_ANCHOR,
            node,
            PATTERN_MESSAGES[PatternType.MISSING_ANCHOR],
            name,
          );
        }
      }
      ts.forEachChild(node, checkNode);
    };
    checkNode(this.sourceFile);
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function scanFile(filePath: string): DefensivePattern[] {
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const ext = path.extname(filePath);
  if (![".ts", ".tsx", ".js", ".jsx", ".mjs"].includes(ext)) {
    throw new Error(`Not a TypeScript/JavaScript file: ${filePath}`);
  }

  const scanner = new Scanner(filePath);
  return scanner.scan();
}

export function scanDirectory(
  dirPath: string,
  recursive: boolean = true,
): Map<string, DefensivePattern[]> {
  const results = new Map<string, DefensivePattern[]>();
  const exts = [".ts", ".tsx", ".js", ".jsx", ".mjs"];

  const scan = (dir: string) => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      // Skip hidden dirs and node_modules
      if (entry.name.startsWith(".") || entry.name === "node_modules") {
        continue;
      }

      if (entry.isDirectory() && recursive) {
        scan(fullPath);
      } else if (entry.isFile() && exts.includes(path.extname(entry.name))) {
        try {
          const patterns = scanFile(fullPath);
          if (patterns.length > 0) {
            results.set(fullPath, patterns);
          }
        } catch {
          // Skip files that can't be scanned
        }
      }
    }
  };

  scan(dirPath);
  return results;
}

export function summarize(patterns: DefensivePattern[]) {
  const byType: Record<string, number> = {};
  const bySeverity: Record<string, number> = {
    error: 0,
    warning: 0,
    info: 0,
  };

  for (const p of patterns) {
    const label = PATTERN_LABELS[p.patternType];
    byType[label] = (byType[label] || 0) + 1;
    bySeverity[PATTERN_SEVERITY[p.patternType]]++;
  }

  return {
    total: patterns.length,
    byType,
    bySeverity,
  };
}

// Re-export for convenience
export { PATTERN_LABELS, PATTERN_SEVERITY, PATTERN_MESSAGES };
