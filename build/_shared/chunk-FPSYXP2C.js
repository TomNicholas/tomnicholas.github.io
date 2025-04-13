import{c as m}from"/build/_shared/chunk-2NH4LW52.js";var h=m((M,d)=>{d.exports=s;s.displayName="textile";s.aliases=[];function s(l){(function(a){var p=/\([^|()\n]+\)|\[[^\]\n]+\]|\{[^}\n]+\}/.source,c=/\)|\((?![^|()\n]+\))/.source;function e(k,b){return RegExp(k.replace(/<MOD>/g,function(){return"(?:"+p+")"}).replace(/<PAR>/g,function(){return"(?:"+c+")"}),b||"")}var i={css:{pattern:/\{[^{}]+\}/,inside:{rest:a.languages.css}},"class-id":{pattern:/(\()[^()]+(?=\))/,lookbehind:!0,alias:"attr-value"},lang:{pattern:/(\[)[^\[\]]+(?=\])/,lookbehind:!0,alias:"attr-value"},punctuation:/[\\\/]\d+|\S/},u=a.languages.textile=a.languages.extend("markup",{phrase:{pattern:/(^|\r|\n)\S[\s\S]*?(?=$|\r?\n\r?\n|\r\r)/,lookbehind:!0,inside:{"block-tag":{pattern:e(/^[a-z]\w*(?:<MOD>|<PAR>|[<>=])*\./.source),inside:{modifier:{pattern:e(/(^[a-z]\w*)(?:<MOD>|<PAR>|[<>=])+(?=\.)/.source),lookbehind:!0,inside:i},tag:/^[a-z]\w*/,punctuation:/\.$/}},list:{pattern:e(/^[*#]+<MOD>*\s+\S.*/.source,"m"),inside:{modifier:{pattern:e(/(^[*#]+)<MOD>+/.source),lookbehind:!0,inside:i},punctuation:/^[*#]+/}},table:{pattern:e(/^(?:(?:<MOD>|<PAR>|[<>=^~])+\.\s*)?(?:\|(?:(?:<MOD>|<PAR>|[<>=^~_]|[\\/]\d+)+\.|(?!(?:<MOD>|<PAR>|[<>=^~_]|[\\/]\d+)+\.))[^|]*)+\|/.source,"m"),inside:{modifier:{pattern:e(/(^|\|(?:\r?\n|\r)?)(?:<MOD>|<PAR>|[<>=^~_]|[\\/]\d+)+(?=\.)/.source),lookbehind:!0,inside:i},punctuation:/\||^\./}},inline:{pattern:e(/(^|[^a-zA-Z\d])(\*\*|__|\?\?|[*_%@+\-^~])<MOD>*.+?\2(?![a-zA-Z\d])/.source),lookbehind:!0,inside:{bold:{pattern:e(/(^(\*\*?)<MOD>*).+?(?=\2)/.source),lookbehind:!0},italic:{pattern:e(/(^(__?)<MOD>*).+?(?=\2)/.source),lookbehind:!0},cite:{pattern:e(/(^\?\?<MOD>*).+?(?=\?\?)/.source),lookbehind:!0,alias:"string"},code:{pattern:e(/(^@<MOD>*).+?(?=@)/.source),lookbehind:!0,alias:"keyword"},inserted:{pattern:e(/(^\+<MOD>*).+?(?=\+)/.source),lookbehind:!0},deleted:{pattern:e(/(^-<MOD>*).+?(?=-)/.source),lookbehind:!0},span:{pattern:e(/(^%<MOD>*).+?(?=%)/.source),lookbehind:!0},modifier:{pattern:e(/(^\*\*|__|\?\?|[*_%@+\-^~])<MOD>+/.source),lookbehind:!0,inside:i},punctuation:/[*_%?@+\-^~]+/}},"link-ref":{pattern:/^\[[^\]]+\]\S+$/m,inside:{string:{pattern:/(^\[)[^\]]+(?=\])/,lookbehind:!0},url:{pattern:/(^\])\S+$/,lookbehind:!0},punctuation:/[\[\]]/}},link:{pattern:e(/"<MOD>*[^"]+":.+?(?=[^\w/]?(?:\s|$))/.source),inside:{text:{pattern:e(/(^"<MOD>*)[^"]+(?=")/.source),lookbehind:!0},modifier:{pattern:e(/(^")<MOD>+/.source),lookbehind:!0,inside:i},url:{pattern:/(:).+/,lookbehind:!0},punctuation:/[":]/}},image:{pattern:e(/!(?:<MOD>|<PAR>|[<>=])*(?![<>=])[^!\s()]+(?:\([^)]+\))?!(?::.+?(?=[^\w/]?(?:\s|$)))?/.source),inside:{source:{pattern:e(/(^!(?:<MOD>|<PAR>|[<>=])*)(?![<>=])[^!\s()]+(?:\([^)]+\))?(?=!)/.source),lookbehind:!0,alias:"url"},modifier:{pattern:e(/(^!)(?:<MOD>|<PAR>|[<>=])+/.source),lookbehind:!0,inside:i},url:{pattern:/(:).+/,lookbehind:!0},punctuation:/[!:]/}},footnote:{pattern:/\b\[\d+\]/,alias:"comment",inside:{punctuation:/\[|\]/}},acronym:{pattern:/\b[A-Z\d]+\([^)]+\)/,inside:{comment:{pattern:/(\()[^()]+(?=\))/,lookbehind:!0},punctuation:/[()]/}},mark:{pattern:/\b\((?:C|R|TM)\)/,alias:"comment",inside:{punctuation:/[()]/}}}}}),t=u.phrase.inside,n={inline:t.inline,link:t.link,image:t.image,footnote:t.footnote,acronym:t.acronym,mark:t.mark};u.tag.pattern=/<\/?(?!\d)[a-z0-9]+(?:\s+[^\s>\/=]+(?:=(?:("|')(?:\\[\s\S]|(?!\1)[^\\])*\1|[^\s'">=]+))?)*\s*\/?>/i;var o=t.inline.inside;o.bold.inside=n,o.italic.inside=n,o.inserted.inside=n,o.deleted.inside=n,o.span.inside=n;var r=t.table.inside;r.inline=n.inline,r.link=n.link,r.image=n.image,r.footnote=n.footnote,r.acronym=n.acronym,r.mark=n.mark})(l)}});export{h as a};
