// EPIC-09 STORY-03: the patcher, in the browser (D-22). It reads the user's ZIP, knows it by its SHA-256
// (window.PATCHES, from src/survey/patches.tsv), applies the fix the table names, checks the result's
// SHA-256, and writes the patched ZIP. The fixes are tools/build_gos5.py's and build_gos4.py's builds,
// GDBPB.PRG, the fastload bit and a file from a second download (D-23), done here byte for byte as the
// Python tools do them: tools/unpack.py's unpacker, tools/pack.py's packer. Standard APIs only. The page
// carries our blocks (window.PATCH_BLOCKS) and no byte of the adaptations (D-11).

const Patcher = (() => {
  'use strict';

  // --- bytes --------------------------------------------------------------------------------------
  const u16 = (b, o) => (b[o] << 8) | b[o + 1];
  const u32 = (b, o) => ((b[o] << 24) >>> 0) + (b[o + 1] << 16) + (b[o + 2] << 8) + b[o + 3];
  const s8 = (v) => (v > 127 ? v - 256 : v);
  const s16 = (b, o) => { const v = u16(b, o); return v > 32767 ? v - 65536 : v; };
  const put16 = (b, o, v) => { b[o] = (v >>> 8) & 255; b[o + 1] = v & 255; };
  const put32 = (b, o, v) => { b[o] = (v >>> 24) & 255; b[o + 1] = (v >>> 16) & 255; b[o + 2] = (v >>> 8) & 255; b[o + 3] = v & 255; };
  const le16 = (b, o) => b[o] | (b[o + 1] << 8);
  const le32 = (b, o) => (b[o] | (b[o + 1] << 8) | (b[o + 2] << 16) | (b[o + 3] << 24)) >>> 0;
  const concat = (parts) => {
    const out = new Uint8Array(parts.reduce((n, p) => n + p.length, 0));
    let o = 0;
    for (const p of parts) { out.set(p, o); o += p.length; }
    return out;
  };
  const latin1 = (b) => {
    let s = '';
    for (let i = 0; i < b.length; i += 8192) s += String.fromCharCode.apply(null, b.subarray(i, i + 8192));
    return s;
  };
  const equal = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);
  const hex = (buf) => [...new Uint8Array(buf)].map((x) => x.toString(16).padStart(2, '0')).join('');
  const sha256 = async (b) => hex(await crypto.subtle.digest('SHA-256', b));
  class PatchError extends Error {}
  const fail = (msg) => { throw new PatchError(msg); };

  // --- ZIP ----------------------------------------------------------------------------------------
  const CRC = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c >>> 0;
    }
    return t;
  })();
  const crc32 = (b) => {
    let c = 0xffffffff;
    for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
  };

  // The central directory's entries, each with its raw (compressed) bytes.
  function readZip(zip) {
    let eocd = -1;
    for (let i = zip.length - 22; i >= Math.max(0, zip.length - 65557); i--) {
      if (le32(zip, i) === 0x06054b50) { eocd = i; break; }
    }
    if (eocd < 0) fail('this is not a ZIP file');
    const count = le16(zip, eocd + 10);
    let p = le32(zip, eocd + 16);
    const entries = [];
    for (let k = 0; k < count; k++) {
      if (le32(zip, p) !== 0x02014b50) fail('the ZIP file is damaged');
      const e = {
        made: le16(zip, p + 4), need: le16(zip, p + 6), flags: le16(zip, p + 8), method: le16(zip, p + 10),
        time: le16(zip, p + 12), date: le16(zip, p + 14), crc: le32(zip, p + 16), csize: le32(zip, p + 20),
        size: le32(zip, p + 24), attrIn: le16(zip, p + 36), attrEx: le32(zip, p + 38), local: le32(zip, p + 42),
      };
      const nlen = le16(zip, p + 28), xlen = le16(zip, p + 30), clen = le16(zip, p + 32);
      e.nameBytes = zip.slice(p + 46, p + 46 + nlen);
      e.name = latin1(e.nameBytes);
      const l = e.local;
      if (le32(zip, l) !== 0x04034b50) fail('the ZIP file is damaged');
      const start = l + 30 + le16(zip, l + 26) + le16(zip, l + 28);
      e.raw = zip.subarray(start, start + e.csize);
      if (e.flags & 1) fail(`${e.name} is encrypted`);
      entries.push(e);
      p += 46 + nlen + xlen + clen;
    }
    return entries;
  }

  async function inflate(e) {
    if (e.method === 0) return e.raw.slice();
    if (e.method !== 8) fail(`${e.name}: a compression this page does not read (${e.method})`);
    const stream = new Blob([e.raw]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
    const out = new Uint8Array(await new Response(stream).arrayBuffer());
    if (out.length !== e.size || crc32(out) !== e.crc) fail(`${e.name}: damaged in the ZIP`);
    return out;
  }

  // The ZIP again: unchanged entries keep their compressed bytes, changed and added ones are stored.
  function writeZip(entries) {
    const locals = [], centrals = [];
    let offset = 0;
    for (const e of entries) {
      const name = e.nameBytes;
      const lh = new Uint8Array(30 + name.length);
      const dv = new DataView(lh.buffer);
      dv.setUint32(0, 0x04034b50, true); dv.setUint16(4, e.need, true); dv.setUint16(6, e.flags & ~8, true);
      dv.setUint16(8, e.method, true); dv.setUint16(10, e.time, true); dv.setUint16(12, e.date, true);
      dv.setUint32(14, e.crc, true); dv.setUint32(18, e.raw.length, true); dv.setUint32(22, e.size, true);
      dv.setUint16(26, name.length, true); lh.set(name, 30);
      const ch = new Uint8Array(46 + name.length);
      const cv = new DataView(ch.buffer);
      cv.setUint32(0, 0x02014b50, true); cv.setUint16(4, e.made, true); cv.setUint16(6, e.need, true);
      cv.setUint16(8, e.flags & ~8, true); cv.setUint16(10, e.method, true); cv.setUint16(12, e.time, true);
      cv.setUint16(14, e.date, true); cv.setUint32(16, e.crc, true); cv.setUint32(20, e.raw.length, true);
      cv.setUint32(24, e.size, true); cv.setUint16(28, name.length, true); cv.setUint16(36, e.attrIn, true);
      cv.setUint32(38, e.attrEx, true); cv.setUint32(42, offset, true); ch.set(name, 46);
      locals.push(lh, e.raw); centrals.push(ch);
      offset += lh.length + e.raw.length;
    }
    const cd = concat(centrals);
    const end = new Uint8Array(22);
    const ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true); ev.setUint16(8, entries.length, true); ev.setUint16(10, entries.length, true);
    ev.setUint32(12, cd.length, true); ev.setUint32(16, offset, true);
    return concat([...locals, cd, end]);
  }

  const stored = (template, data, name) => {
    const nameBytes = name ? Uint8Array.from(name, (c) => c.charCodeAt(0)) : template.nameBytes;
    // an added file takes the archive's first entry's date and system, and a plain file's attributes
    return { ...template, nameBytes, name: name || template.name, method: 0, flags: 0, need: 10, raw: data,
             size: data.length, crc: crc32(data), attrIn: name ? 0 : template.attrIn,
             attrEx: name ? 0x20 : template.attrEx };
  };

  // --- the Gamex launcher's packer (tools/unpack.py, tools/pack.py) ---------------------------------
  function depack(src, start) {
    const out = [];
    let i = start;
    for (;;) {
      const c = src[i++];
      if (c === undefined) fail('the packed program ends early');
      if (c === 0) return Uint8Array.from(out);
      if (c < 0x80) { for (let k = 0; k < c; k++) out.push(src[i + k]); i += c; continue; }
      let dist, length;
      if (c & 0x40) { dist = (src[i] << 8) | src[i + 1]; i += 2; length = (c & 0x3f) + 4; }
      else { dist = src[i]; i += 1; length = (c & 0x3f) + 3; }
      if (!(dist > 0 && dist <= out.length)) fail('the packed program is damaged');
      for (let k = 0; k < length; k++) out.push(out[out.length - dist]);
    }
  }

  function ficHeader(d) {
    if (d[0] !== 0x43 || d[1] !== 0x33) fail("no 'C3' header");
    return { packed: u32(d, 2), unpacked: u32(d, 6) };
  }

  function unpackFic(d) {
    const h = ficHeader(d);
    if (d.length < 32 + h.packed || d.subarray(32 + h.packed).some((x) => x)) fail('the packed program has a wrong size');
    const out = depack(d, 32);
    if (out.length !== h.unpacked) fail('the packed program unpacks to a wrong size');
    return out;
  }

  function unpackStart(d) {
    if (u16(d, 0) !== 0x601a) fail('not a GEMDOS program');
    const tlen = u32(d, 2), dlen = u32(d, 6);
    const payload = d.subarray(28 + tlen, 28 + tlen + dlen);
    const packed = ficHeader(payload).packed;
    const pad = payload.subarray(32 + packed);
    if (pad.length > 3 || pad.some((x) => x)) fail('unexpected bytes after the packed program');
    return unpackFic(payload.subarray(0, 32 + packed));
  }

  const MAX_LIT = 127, SHORT_DIST = 255, LONG_DIST = 65535, SHORT_MAX = 0x3f + 3, LONG_MAX = 0x3f + 4, CHAIN = 512;

  function matches(data) {
    const n = data.length, heads = new Map(), found = new Array(n);
    for (let i = 0; i < n; i++) {
      const full = i + 3 <= n;
      const key = full ? (data[i] << 16) | (data[i + 1] << 8) | data[i + 2] : -1;
      let cands = [];
      if (full) { cands = heads.get(key); if (!cands) { cands = []; heads.set(key, cands); } }
      let sLen = 0, sDist = 0, lLen = 0, lDist = 0;
      const limitS = Math.min(SHORT_MAX, n - i), limitL = Math.min(LONG_MAX, n - i);
      const lo = Math.max(0, cands.length - CHAIN);
      for (let c = cands.length - 1; c >= lo; c--) {
        const j = cands[c], dist = i - j;
        if (dist > LONG_DIST) break;
        let length = 0;
        const max = Math.min(limitL, n - j);
        while (length < max && data[j + length] === data[i + length]) length++;
        if (dist <= SHORT_DIST && length > sLen) { sLen = Math.min(length, limitS); sDist = dist; }
        if (length > lLen) { lLen = length; lDist = dist; }
        if (lLen === limitL && (sLen === limitS || dist > SHORT_DIST)) break;
      }
      found[i] = [sLen >= 3 ? sLen : 0, sDist, lLen >= 4 ? lLen : 0, lDist];
      if (full) cands.push(i);
    }
    return found;
  }

  function pack(data) {
    const n = data.length, found = matches(data), INF = Number.MAX_SAFE_INTEGER;
    const cost = new Array(n + 1).fill(INF), step = new Array(n + 1);
    cost[n] = 1;
    const win = [];
    let head = 0;
    for (let i = n - 1; i >= 0; i--) {
      const j = i + 1;
      while (win.length > head && cost[win[win.length - 1]] + win[win.length - 1] >= cost[j] + j) win.pop();
      win.push(j);
      while (win[head] > i + MAX_LIT) head++;
      let best = cost[win[head]] + win[head] - i + 1, how = [0, win[head] - i];
      const [sLen, sDist, lLen, lDist] = found[i];
      for (let length = 3; length <= sLen; length++) {
        if (cost[i + length] + 2 < best) { best = cost[i + length] + 2; how = [1, length, sDist]; }
      }
      for (let length = 4; length <= lLen; length++) {
        if (cost[i + length] + 3 < best) { best = cost[i + length] + 3; how = [2, length, lDist]; }
      }
      cost[i] = best; step[i] = how;
    }
    const out = [];
    for (let i = 0; i < n;) {
      const how = step[i];
      if (how[0] === 0) { out.push(how[1]); for (let k = 0; k < how[1]; k++) out.push(data[i + k]); i += how[1]; }
      else if (how[0] === 1) { out.push(0x80 | (how[1] - 3), how[2]); i += how[1]; }
      else { out.push(0xc0 | (how[1] - 4), how[2] >> 8, how[2] & 255); i += how[1]; }
    }
    out.push(0);
    const stream = Uint8Array.from(out);
    if (stream.length !== cost[0] || !equal(depack(stream, 0), data)) fail('internal: the packer failed');
    return stream;
  }

  const STUB_TEXT_DATA = 28 + 0x08, STUB_TOP = 28 + 0x10, STUB_LONGS = 28 + 0x18;

  function inPlaceMargin(stream, top) {
    let read = top - stream.length, write = -28, i = 0, margin = top;
    for (;;) {
      const c = stream[i];
      const size = c === 0 ? 1 : c < 0x80 ? 1 + c : c & 0x40 ? 3 : 2;
      const produced = c === 0 ? 0 : c < 0x80 ? c : (c & 0x3f) + (c & 0x40 ? 4 : 3);
      read += size; write += produced; i += size;
      margin = Math.min(margin, read - write);
      if (c === 0) return margin;
    }
  }

  function buildStart(prog, like) {
    const stream = pack(prog);
    const ph = new Uint8Array(32);
    ph[0] = 0x43; ph[1] = 0x33; put32(ph, 2, stream.length); put32(ph, 6, prog.length);
    ph.set(like.subarray(28 + 230 + 10, 28 + 230 + 32), 10);
    ph.set(prog.subarray(10, 14), 10);
    let data = concat([ph, stream]);
    const padn = ((-(data.length - 32) % 4) + 4) % 4;
    data = concat([data, new Uint8Array(padn)]);
    const stub = like.slice(0, 28 + 230);
    let top = u32(stub, STUB_TOP);
    let margin = inPlaceMargin(data.subarray(32), top);
    if (margin < 0) { top += (-margin + 3) & ~3; put32(stub, STUB_TOP, top); margin = inPlaceMargin(data.subarray(32), top); }
    if (margin < 0) fail('internal: the packed program would overwrite itself');
    put32(stub, 6, data.length);
    put32(stub, STUB_TEXT_DATA, 230 + data.length);
    put32(stub, STUB_LONGS, (data.length - 32) / 4);
    return concat([stub, data, new Uint8Array(4)]);
  }

  // --- the GOS5 and GOS4 builds (tools/build_gos5.py, tools/build_gos4.py) --------------------------
  const GD_CHECK = 46, GD_INFO = 20;
  const AREAS = { 0xc0100: [0xb7180, 0xb7100], 0x1a0100: [0x197180, 0x197100], 0x1c0100: [0x1b7180, 0x1b7100] };
  const CHECK = /\x22\x78\x04\x72\x0c\xa9PPHD\xff\xf8\x66([\s\S])([\s\S]{2})?/g;
  const IMAGE = /\x2c\x79([\s\S]{4})\xdd\xfc([\s\S]{4})/g;
  const END_A = /\x42\x99\x22\xc3\x42\x99\x42\x99\x22\x8a\x60\x00([\s\S]{2})/g;
  const AFTER_B = /\x41\xf9([\s\S]{4})\x70\x00\x30\x28\x00\x0c\xd1\xc0\x4e\x90\x60\x00([\s\S]{2})/y;
  const END_4 = /\x42\x99\x22\xc3\x42\x99\x42\x99\x22\x8a\x60(?:\x00([\s\S]{2})|([^\x00]))/g;
  const TABLE = /\x4d\xf9([\s\S]{4})(?:\x23\xce([\s\S]{4})|\x21\xce([\s\S]{2}))/g;
  const JMP = /\x4e\xf9(\x00[\x0c\x1c]\x01\x00)/g;
  const CLEAR = '\x1bE\x1bY0 \x00';
  const VSYNC = [0x3f, 0x3c, 0x00, 0x25, 0x4e, 0x4e, 0x54, 0x8f];
  const bytesOf = (s) => Uint8Array.from(s, (c) => c.charCodeAt(0));

  function even(re, s) {
    re.lastIndex = 0;
    const out = [];
    let m;
    while ((m = re.exec(s)) !== null) {
      if (m.index % 2 === 0) out.push(m);
      if (m[0].length === 0) re.lastIndex++;
    }
    return out;
  }

  function check(text, s) {
    const checks = even(CHECK, s);
    if (checks.length !== 1) fail(`${checks.length} PPHD checks, not one`);
    const m = checks[0];
    const short = m[1] !== '\x00';
    const end = m.index + (short ? 14 : 16);
    const disp = short ? s8(m[1].charCodeAt(0)) : s16(bytesOf(m[2]), 0);
    return { check: m.index, check_end: end, pp: end, no_pp: m.index + 14 + disp };
  }

  function infoScreen(text, s) {
    const target = (at) => at + 2 + s16(text, at + 2);
    const strings = new Set();
    for (let k = s.indexOf(CLEAR); k >= 0; k = s.indexOf(CLEAR, k + CLEAR.length)) strings.add(k);
    const infos = [], calls = [];
    for (let k = 0; k < text.length - 4; k += 2) if (text[k] === 0x41 && text[k + 1] === 0xfa && strings.has(target(k))) infos.push(k);
    const set = new Set(infos);
    for (let k = 8; k < text.length - 4; k += 2) {
      if (text[k] === 0x61 && text[k + 1] === 0x00 && set.has(target(k)) && VSYNC.every((v, x) => text[k - 8 + x] === v)) calls.push(k);
    }
    if (infos.length !== 1 || calls.length !== 1) fail(`the info screen: ${infos.length} show_info, ${calls.length} calls, not one`);
    return [infos[0], calls[0]];
  }

  function findGos5(text) {
    const s = latin1(text), f = check(text, s);
    const images = new Set();
    for (const i of even(IMAGE, s)) {
      const a = u32(bytesOf(i[1]), 0), b = u32(bytesOf(i[2]), 0);
      if (b - a === 0x1a) images.add(`${a},${b}`);
    }
    if (images.size !== 1) fail(`GOS's image pointer: ${images.size}, not one`);
    const [img, imgAdd] = [...images][0].split(',').map(Number);
    f.img = img; f.img_add = imgAdd; f.gos = imgAdd - 0x700;
    AFTER_B.lastIndex = f.check_end;
    const after = AFTER_B.exec(s);
    if (after && u32(bytesOf(after[1]), 0) === f.gos) {
      f.gos_start = f.check_end + 18 + s16(bytesOf(after[2]), 0);
    } else {
      const ends = even(END_A, s).filter((e) => e.index > f.check_end);
      if (!ends.length) fail("GOS's start: no end of set_buffers after the check");
      f.gos_start = ends[0].index + 12 + s16(bytesOf(ends[0][1]), 0);
    }
    [f.info, f.info_call] = infoScreen(text, s);
    if (!AREAS[f.gos]) fail(`GOS at $${f.gos.toString(16)}: no place known for the forwarder`);
    [f.run, f.md_stack] = AREAS[f.gos];
    f.params = [f.gos, f.img, f.img_add, f.run, f.md_stack];
    return f;
  }

  function findGos4(text) {
    const s = latin1(text), f = check(text, s);
    const ends = even(END_4, s).filter((e) => e.index > f.check_end);
    if (!ends.length) fail("the end of the launcher's path: none after the check");
    const e = ends[0];
    f.gos_start = e.index + 12 + (e[1] !== undefined ? s16(bytesOf(e[1]), 0) : s8(e[2].charCodeAt(0)));
    const tables = even(TABLE, s).filter((t) => t.index >= f.check_end && t.index < e.index);
    if (tables.length !== 1) fail(`the driver table: ${tables.length}, not one`);
    const t = tables[0];
    f.table = u32(bytesOf(t[1]), 0);
    f.table_ptr = t[2] !== undefined ? u32(bytesOf(t[2]), 0) : u16(bytesOf(t[3]), 0);
    const jmps = even(JMP, s);
    if (jmps.length !== 1 || jmps[0].index < f.gos_start) fail(`the jump into GOS: ${jmps.length}, not one`);
    f.gos = u32(bytesOf(jmps[0][1]), 0);
    [f.info, f.info_call] = infoScreen(text, s);
    if (!AREAS[f.gos]) fail(`GOS at $${f.gos.toString(16)}: no place known for the forwarder`);
    [f.run, f.md_stack] = AREAS[f.gos];
    f.params = [f.gos, f.table, f.table_ptr, f.run, f.md_stack];
    return f;
  }

  function relocations(prog, tlen, dlen, slen) {
    let table = 28 + tlen + dlen + slen;
    const first = u32(prog, table);
    if (!first) return [];
    const out = [first];
    let pos = first, i = table + 4;
    for (;;) {
      const st = prog[i++];
      if (st === 0) return out;
      if (st === 1) { pos += 254; continue; }
      pos += st; out.push(pos);
    }
  }

  function encode(positions) {
    if (!positions.length) return new Uint8Array(4);
    const out = [];
    const h = new Uint8Array(4); put32(h, 0, positions[0]); out.push(...h);
    for (let k = 1; k < positions.length; k++) {
      let st = positions[k] - positions[k - 1];
      while (st > 254) { out.push(1); st -= 254; }
      out.push(st);
    }
    out.push(0);
    return Uint8Array.from(out);
  }

  function build(prog, block, f, floppy) {
    const tlen = u32(prog, 2), dlen = u32(prog, 6), slen = u32(prog, 14);
    const relocs = relocations(prog, tlen, dlen, slen);
    if (relocs.some((p) => (f.check <= p && p < f.check_end) || (f.info_call - 3 <= p && p < f.info_call + 4))) {
      fail('a relocation inside the PPHD check or the info screen\'s call');
    }
    const d = block.length;
    const body = concat([block, prog.subarray(28, 28 + tlen + dlen)]);
    const branch = (at, target) => {
      const disp = target - (at + 2);
      if (disp < -0x8000 || disp >= 0x8000) fail('a branch out of reach');
      body[at] = 0x60; body[at + 1] = 0; put16(body, at + 2, disp & 0xffff);
    };
    branch(0, d); branch(4, f.pp + d); branch(8, f.no_pp + d); branch(12, f.gos_start + d); branch(16, f.info + d);
    f.params.forEach((v, k) => put32(body, 24 + 4 * k, v));
    put16(body, 44, floppy ? 1 : 0);
    const call = f.info_call + d;
    put16(body, call + 2, (GD_INFO - (call + 2)) & 0xffff);
    const site = f.check + d;
    branch(site, GD_CHECK);
    for (let at = site + 4; at < f.check_end + d; at += 2) { body[at] = 0x4e; body[at + 1] = 0x71; }
    const moved = relocs.map((p) => p + d);
    for (const p of moved) put32(body, p, (u32(body, p) + d) >>> 0);
    const header = prog.slice(0, 28);
    put32(header, 2, tlen + d);
    const symbols = prog.subarray(28 + tlen + dlen, 28 + tlen + dlen + slen);
    return concat([header, body, symbols, encode(moved)]);
  }

  function launcher(original) {
    try { return [unpackStart(original), true]; }
    catch (err) {
      if (u16(original, 0) === 0x601a && /\x22\x78\x04\x72\x0c\xa9PPHD\xff\xf8\x66/.test(latin1(original))) return [original, false];
      throw err;
    }
  }

  function buildGos(original, kind, floppy) {
    const block = kind === 'gos4' ? window.PATCH_BLOCKS.gos4 : window.PATCH_BLOCKS.gos5;
    if (u32(block, GD_CHECK) !== 0x22780472 || u16(block, GD_INFO) !== 0x6000 || block.length % 2) fail('internal: a wrong block');
    const [prog, packed] = launcher(original);
    const text = prog.subarray(28, 28 + u32(prog, 2));
    const f = kind === 'gos4' ? findGos4(text) : findGos5(text);
    const fresh = build(prog, block, f, floppy);
    if (!packed) return fresh;
    const out = buildStart(fresh, original);
    if (!equal(unpackStart(out), fresh)) fail('internal: the packed result does not unpack to the build');
    return out;
  }

  // --- the patch ----------------------------------------------------------------------------------
  const b64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
  const byName = (entries, name) => entries.find((e) => e.name.toUpperCase() === name.toUpperCase());

  // What the table says about a ZIP, by its SHA-256.
  async function identify(zip) {
    const digest = await sha256(zip);
    return { digest, row: window.PATCHES.find((r) => r.sha256 === digest) || null };
  }

  // The patched ZIP, or a PatchError. second: the second download's bytes, when row.needs.
  async function patch(zip, row, second) {
    const entries = readZip(zip);
    const out = entries.slice();
    const opts = (row.options || '').split(' ').filter(Boolean);
    if (row.action === 'gos5' || row.action === 'gos4' || row.action === 'fastload') {
      const e = byName(entries, row.target);
      if (!e) fail(`${row.target} is not in the ZIP`);
      const original = await inflate(e);
      if ((await sha256(original)) !== row.target_sha256) fail(`${row.target} is not the expected file`);
      let result;
      if (row.action === 'fastload') { result = original.slice(); result[25] |= 1; }
      else result = buildGos(original, row.action, opts.includes('--floppy'));
      if ((await sha256(result)) !== row.result_sha256) fail('the result is not our build: nothing written');
      out[out.indexOf(e)] = stored(e, result);
    } else if (row.action === 'gdbpb') {
      const prg = window.PATCH_BLOCKS.gdbpb;
      if ((await sha256(prg)) !== row.result_sha256) fail('internal: GDBPB.PRG is not the expected build');
      if (byName(entries, row.target)) fail(`${row.target} is in the ZIP already`);
      out.push(stored(entries[0], prg, row.target));
    } else if (row.action !== 'rody2') {
      fail('nothing to patch');
    }
    if (row.needs) {
      if (!second) fail(`this game needs ${row.needs} too`);
      if ((await sha256(second)) !== row.needs_sha256) fail(`the second file is not ${row.needs}`);
      const other = readZip(second);
      for (const item of row.add.split(',')) {
        const [path, digest] = item.split('=');
        const base = path.split('/').pop().toUpperCase();
        const from = other.find((e) => e.name.split('/').pop().toUpperCase() === base);
        if (!from) fail(`${base} is not in ${row.needs}`);
        const data = await inflate(from);
        if ((await sha256(data)) !== digest) fail(`${base} in ${row.needs} is not the expected file`);
        const there = byName(out, path);
        if (there) out[out.indexOf(there)] = stored(there, data);
        else out.push(stored(entries[0], data, path));
      }
    }
    return writeZip(out);
  }

  return { identify, patch, readZip, inflate, sha256, PatchError, b64, _test: { depack, pack, unpackStart, buildGos } };
})();
window.Patcher = Patcher;

// --- the page (build_site.py's patch.html) ----------------------------------------------------------
(() => {
  const form = document.querySelector('.patcher');
  if (!form) return;
  const input = form.querySelector('#patch-zip');
  const out = form.querySelector('.patch-result');
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const games = (row) => (row.games && row.games.length ? row.games.join(' and ') : row.archive);
  const say = (html) => { out.innerHTML = html; };
  const start = (row) => (row.start ? ` Start it with <code>${esc(row.start.split('/').pop())}</code>${
    row.start.includes('/') ? ` in its folder <code>${esc(row.start.split('/').slice(0, -1).join('/'))}</code>` : ''}.` : '');
  let zip = null, row = null, name = '';
  const file = (path) => `<code>${esc(String(path || '').split('/').pop())}</code>`;
  const changed = (r) => ({
    gos5: `Its start program ${file(r.target)} is rebuilt, so that the game reads its files from GEMDOS and GEMDRIVE by name.`,
    gos4: `Its start program ${file(r.target)} is rebuilt, so that the game reads its files from GEMDOS and GEMDRIVE by name.`,
    gdbpb: '<code>GDBPB.PRG</code> is added to its folder: it gives the drive the description the game asks for.',
    fastload: `The fastload bit is set in ${file(r.target)}, so that the program that starts it is not ended.`,
    rody2: 'The start program it lacks, <code>RUNME.TOS</code> from Rody and Mastico 4, is added to its folder.',
  }[r.action] || '') + (r.needs && r.action !== 'rody2' ? ` The files it needs from <code>${esc(r.needs)}</code> are added too.` : '')
    + ((r.options || '').includes('--floppy') ? ' Keep any floppy disk in drive A while it runs.' : '');
  const row0 = (r) => r.rows && `catalogue.html#g-${String(r.rows.split(';')[0]).padStart(4, '0')}`;
  const why = (r) => /^unsure/.test(r.reason) ? 'Its runs did not settle whether it can run from GEMDOS and GEMDRIVE.'
    : /^not feasible/.test(r.reason) ? 'It cannot run from GEMDOS and GEMDRIVE without changing the game itself.'
    : /^built, but/.test(r.reason) ? 'Its fix is built, but the game still fails with it.'
    : 'Its fix is not built yet.';

  const offer = (bytes) => {
    const file = name.replace(/\.zip$/i, '') + '-GEMDRIVE.ZIP';
    const url = URL.createObjectURL(new Blob([bytes], { type: 'application/zip' }));
    const first = row.action === 'gdbpb' ? ` Run <code>GDBPB.PRG</code> from the game's folder first, once after each reset or power-on.` : '';
    say(`<p><strong>${esc(games(row))}: patched.</strong> ${changed(row)}</p>
<p>${start(row)}${first}</p>
<p class="ask"><a class="button default" href="${url}" download="${esc(file)}">Download ${esc(file)}</a></p>`);
  };

  const run = async (second) => {
    try {
      say('<p>Patching…</p>');
      offer(await Patcher.patch(zip, row, second));
    } catch (e) {
      say(`<p><strong>Not patched.</strong> ${esc(e.message || e)}.</p>`);
    }
  };

  const take = async (file) => {
    if (!file) return;
    name = file.name;
    say('<p>Checking…</p>');
    zip = new Uint8Array(await file.arrayBuffer());
    ({ row } = await Patcher.identify(zip));
    if (!row) {
      say(`<p><strong>This page does not know this file.</strong> It needs a game's ZIP exactly as downloaded
from the 8bitchip.info website, not unpacked and packed again, nor renamed inside.</p>`);
      return;
    }
    const what = {
      none: () => say(`<p><strong>${esc(games(row))} runs from GEMDOS and GEMDRIVE as it is.</strong> Nothing to
patch: copy its folder from the ZIP to your drive.${start(row)}</p>`),
      refuse: () => say(`<p><strong>${esc(games(row))}: no fix yet.</strong> ${why(row)}
<a href="${row0(row)}">Its row in the catalogue</a> says more.</p>`),
      other: () => {
        const main = window.PATCHES.find((x) => x.action !== 'other' && x.action !== 'notgame' && x.rows
          && x.rows.split(';').some((n) => row.rows.split(';').includes(n)));
        say(`<p><strong>This is another download of ${esc(games(row))}.</strong> The page checks the game's main
download${main ? `, <code>${esc(main.archive)}</code>` : ''}, the one its verdict is from: give it that one.</p>`);
      },
      notgame: () => say('<p><strong>This ZIP is on the 8bitchip.info website, but it is not one of the games of the list.</strong></p>'),
    }[row.action];
    if (what) { what(); return; }
    if (row.needs) {
      say(`<p><strong>${esc(games(row))} needs a second download too: <code>${esc(row.needs)}</code></strong>, from
the same website. The fix takes files from it. Choose it here:</p>
<p class="ask"><input id="patch-second" type="file" accept=".zip,.ZIP,application/zip"></p>`);
      out.querySelector('#patch-second').addEventListener('change', async (e) => {
        const f = e.target.files[0];
        if (f) run(new Uint8Array(await f.arrayBuffer()));
      });
      return;
    }
    run(null);
  };

  input.addEventListener('change', () => take(input.files[0]));
  form.addEventListener('dragover', (e) => { e.preventDefault(); form.classList.add('over'); });
  form.addEventListener('dragleave', () => form.classList.remove('over'));
  form.addEventListener('drop', (e) => {
    e.preventDefault();
    form.classList.remove('over');
    take(e.dataTransfer.files[0]);
  });
  form.addEventListener('submit', (e) => e.preventDefault());
})();
