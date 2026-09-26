// 对抗性测试夹具：故意混入各类块内声明与"会骗过括号计数"的构造
// 期望：所有标 SHOULD-FLAG 的行都被报出；标 SAFE 的不报

function outer(a) {
  // SAFE: 函数最外层
  const topLevel = 1
  let topLet = 2

  if (a) {
    const inIf = 3                    // SHOULD-FLAG
    let inIfLet = 4                   // SHOULD-FLAG
  }

  if (a && a > 1
      && a < 9) {                     // 多行条件：{} 所在行的前缀不含关键字
    const inMultilineIf = 5           // SHOULD-FLAG
  }

  for (let i = 0; i < 3; i++) {
    const inFor = 6                   // SHOULD-FLAG
  }

  while (a) {
    const inWhile = 7                 // SHOULD-FLAG
  }

  try {
    const inTry = 8                   // SHOULD-FLAG
  } catch (e) {
    const inCatch = 9                 // SHOULD-FLAG
  }

  switch (a) {
    case 1:
      const inCase = 10               // SHOULD-FLAG
      break
    default:
      break
  }

  do {
    const inDo = 11                   // SHOULD-FLAG
  } while (a)

  // SAFE: 箭头函数体最外层
  const arrow = () => {
    const inArrowBody = 12
    return inArrowBody
  }
  const arrowExpr = (x) => { const inArrowExpr = 13; return inArrowExpr }

  // SAFE: 具名内层函数体最外层
  function inner() {
    const inInnerBody = 14
    return inInnerBody
  }

  // SAFE: 块外声明
  const notInBlock = 15

  // 陷阱 1：模板串里出现引号与花括号（不应破坏追踪）
  const tpl = `he said "hi" { not a block } ${a}`
  if (a) {
    const afterTpl = 16               // SHOULD-FLAG
  }

  // 陷阱 2：字符串里出现 // 与 /*（不应被当成注释）
  const tricky = 'http://x // not a comment /* neither */'
  if (a) {
    const afterTricky = 17            // SHOULD-FLAG
  }

  // 陷阱 3：注释里出现花括号与引号（不应破坏追踪）
  // if (a) { const commented = 1 }
  /* multi { line } comment " with quote */
  if (a) {
    const afterComment = 18           // SHOULD-FLAG
  }

  // 陷阱 4：正则字面量（内含花括号，仍有配平）
  const re = /a{2,3}/g
  if (a) {
    const afterRegex = 19             // SHOULD-FLAG
  }

  // 陷阱 5：解构声明（当前扫描器可能漏）
  if (a) {
    const { d1, d2 } = a              // SHOULD-FLAG（解构）
  }
  if (a) {
    const [e1, e2] = a                // SHOULD-FLAG（数组解构）
  }

  // 陷阱 6：块内声明但同名于外层（重声明风险最高的写法）
  if (a) {
    const shadow = 20                 // SHOULD-FLAG
  }

  // 陷阱 7：单行 if 无花括号（无块 → SAFE）
  if (a) topLet = 21

  // 陷阱 8：for-of / for-in 头部的 let（头部安全）
  const arr = [1, 2]
  for (const v of arr) {
    const inForOf = 22                // SHOULD-FLAG
  }

  return [topLevel, topLet, arrow, arrowExpr, inner, notInBlock, tpl, tricky, re]
}