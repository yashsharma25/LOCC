// https://www.json.org/json-en.html
Prism.languages.qasm = {
  'registerdeclaration': {
		pattern: /(^|[^\\])(qreg|creg)(?=\s*)/,
		lookbehind: true,
		greedy: true
	},
  'gatename': {
		pattern: /(^|[^\\])((r|cr|c)(x|y|z)|measure)(?\s)/,
		lookbehind: true,
		greedy: true
	},
	'property': {
		pattern: /(^|[^\\])"(?:\\.|[^\\"\r\n])*"(?=\s*:)/,
		lookbehind: true,
		greedy: true
	},
	'string': {
		pattern: /(^|[^\\])"(?:\\.|[^\\"\r\n])*"(?!\s*:)/,
		lookbehind: true,
		greedy: true
	},
	'comment': {
		pattern: /\/\/.*|\/\*[\s\S]*?(?:\*\/|$)/,
		greedy: true
	},
	'number': /-?\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b/i,
	'punctuation': /[{}[\],]/,
	'operator': /:/,
	'boolean': /\b(?:false|true)\b/,
	'null': {
		pattern: /\bnull\b/,
		alias: 'keyword'
	}
};
