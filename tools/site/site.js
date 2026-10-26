// EPIC-03 STORY-07: the map's readout, the catalogue's filters and screenshot viewer, and the
// page contents folded on narrow screens. Every page works without it.

const readout = document.querySelector('.readout');
if (readout) {
  const idle = readout.textContent;
  const bands = document.querySelector('.bands');
  bands.addEventListener('mouseover', (e) => {
    const a = e.target.closest('.squares a');
    if (!a) return;
    const cut = a.title.lastIndexOf(': ');
    const strategy = a.closest('.band').querySelector('.label span').textContent;
    readout.textContent = `${a.title.slice(0, cut)}, ${strategy}: ${a.title.slice(cut + 2)}.`;
  });
  bands.addEventListener('mouseleave', () => { readout.textContent = idle; });
}

const form = document.querySelector('.filters');
if (form) {
  const rows = [...document.querySelectorAll('.catalogue tbody tr')];
  const shown = document.getElementById('shown');
  const empty = document.querySelector('.empty');
  const keys = ['q', 'v', 's', 'c', 'r'];

  const apply = (keep) => {
    const f = Object.fromEntries(keys.map((k) => [k, String(new FormData(form).get(k) || '').trim()]));
    const q = f.q.toLowerCase();
    let count = 0;
    for (const tr of rows) {
      const d = tr.dataset;
      const show = (!q || d.n.includes(q)) && (!f.v || d.v === f.v) && (!f.s || d.s === f.s)
        && (!f.c || d.c === f.c) && (!f.r || d.r === f.r);
      tr.hidden = !show;
      if (show) count += 1;
    }
    shown.textContent = count.toLocaleString('en');
    empty.hidden = count > 0;
    if (keep) {
      const p = new URLSearchParams();
      keys.forEach((k) => { if (f[k]) p.set(k, f[k]); });
      history.replaceState(null, '', p.toString() ? `#${p}` : location.pathname);
    }
  };

  const clear = () => {
    keys.forEach((k) => { form.elements[k].value = ''; });
  };

  const fromHash = () => {
    // the home page's check sends ?q=name; the filters live in the hash from then on
    const h = location.hash.slice(1) || location.search.slice(1);
    clear();
    if (h.startsWith('g-')) {
      apply(false);
      document.getElementById(h)?.scrollIntoView();
      return;
    }
    for (const [k, v] of new URLSearchParams(h)) {
      if (keys.includes(k) && form.elements[k]) form.elements[k].value = v;
    }
    apply(false);
  };

  form.addEventListener('input', () => apply(true));
  form.addEventListener('submit', (e) => e.preventDefault());
  form.addEventListener('reset', () => setTimeout(() => apply(true)));
  document.querySelector('.empty .clear').addEventListener('click', () => { form.reset(); });
  window.addEventListener('hashchange', fromHash);
  fromHash();

  const viewer = document.querySelector('.viewer');
  document.addEventListener('click', (e) => {
    const shot = e.target.closest('.shot');
    if (!shot) return;
    const tr = shot.closest('tr');
    const name = tr.querySelector('.game > a').textContent;
    const img = viewer.querySelector('img');
    img.src = shot.dataset.src;
    img.alt = `${name}, the last screen of its run`;
    viewer.querySelector('p').textContent = `${name}: ${tr.dataset.v}. The last screen of its run from the GEMDOS drive.`;
    viewer.showModal();
  });
  viewer.addEventListener('click', (e) => { if (e.target === viewer) viewer.close(); });
}

if (matchMedia('(max-width: 62rem)').matches) {
  document.querySelectorAll('.toc').forEach((d) => { d.open = false; });
}
