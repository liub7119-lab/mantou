/**
 * 节次格式化：统一为 1-2、6-7 等形式
 */
export function formatPeriod(period) {
  if (!period) return ''
  let s = String(period).trim().replace(/节/g, '').replace(/\s/g, '')
  s = s.replace(/[一—–~～至]/g, '-')
  if (/^\d+-\d+(-\d+)?$/.test(s)) return s
  const pairs = ['1-2', '3-4', '5-6', '6-7', '7-8', '8-9', '10-11']
  if (/^\d+$/.test(s)) {
    const n = parseInt(s, 10)
    for (const pair of pairs) {
      const [a, b] = pair.split('-').map(Number)
      if (n === a || n === b) return pair
    }
    if (n % 2 === 1 && n < 11) return `${n}-${n + 1}`
    if (n === 5) return '5-6'
    if (n === 11) return '10-11'
  }
  return s
}
