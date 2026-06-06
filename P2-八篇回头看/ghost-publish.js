const https = require('https');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const GHOST_URL = process.env.GHOST_URL || "https://www.ileemoo.com";
const GHOST_KEY = process.env.GHOST_ADMIN_API_KEY;
const POST_DIR = path.resolve(__dirname);
const IMG_DIR = path.join(POST_DIR, 'xhs-publish-pack', 'images');

function jwtFromKey(keyStr) {
  const [id, secret] = keyStr.split(':');
  const crypto = require('crypto');
  const b64url = (buf) => buf.toString('base64url');
  const h = b64url(Buffer.from(JSON.stringify({ alg: 'HS256', kid: id, typ: 'JWT' })));
  const now = Math.floor(Date.now() / 1000);
  const p = b64url(Buffer.from(JSON.stringify({ iat: now, exp: now + 5 * 60, aud: '/admin/' })));
  const s = crypto.createHmac('sha256', Buffer.from(secret, 'hex')).update(`${h}.${p}`).digest('base64url');
  return `${h}.${p}.${s}`;
}

function apiPost(pathname, body) {
  return new Promise((resolve, reject) => {
    const url = new URL(pathname, GHOST_URL);
    const data = JSON.stringify(body);
    const opts = {
      hostname: url.hostname, path: url.pathname + url.search, method: 'POST',
      headers: { 'Authorization': `Ghost ${jwtFromKey(GHOST_KEY)}`, 'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data), 'Accept-Version': 'v5.73' }
    };
    const req = https.request(opts, res => { let b=''; res.on('data',c=>b+=c); res.on('end',()=>{ try { resolve(JSON.parse(b)); } catch { reject(new Error(b)); }}); });
    req.on('error', reject); req.write(data); req.end();
  });
}

function apiPut(pathname, body) {
  return new Promise((resolve, reject) => {
    const url = new URL(pathname, GHOST_URL);
    const data = JSON.stringify(body);
    const opts = {
      hostname: url.hostname, path: url.pathname + url.search, method: 'PUT',
      headers: { 'Authorization': `Ghost ${jwtFromKey(GHOST_KEY)}`, 'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data), 'Accept-Version': 'v5.73' }
    };
    const req = https.request(opts, res => { let b=''; res.on('data',c=>b+=c); res.on('end',()=>{ try { resolve(JSON.parse(b)); } catch { reject(new Error(b)); }}); });
    req.on('error', reject); req.write(data); req.end();
  });
}

function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    const boundary = '----B' + Math.random().toString(36).slice(2);
    const fileData = fs.readFileSync(filePath);
    const fn = path.basename(filePath);
    const body = Buffer.concat([
      Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${fn}"\r\nContent-Type: image/jpeg\r\n\r\n`, 'utf-8'),
      fileData,
      Buffer.from(`\r\n--${boundary}--\r\n`, 'utf-8')
    ]);
    const url = new URL('/ghost/api/admin/images/upload/', GHOST_URL);
    const opts = {
      hostname: url.hostname, path: url.pathname, method: 'POST',
      headers: { 'Authorization': `Ghost ${jwtFromKey(GHOST_KEY)}`, 'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length, 'Accept-Version': 'v5.73' }
    };
    const req = https.request(opts, res => { let d=''; res.on('data',c=>d+=c); res.on('end',()=>{ try { resolve(JSON.parse(d)); } catch { reject(new Error(d)); }}); });
    req.on('error', reject); req.write(body); req.end();
  });
}

async function main() {
  if (!GHOST_KEY) { console.error('❌ GHOST_ADMIN_API_KEY not set'); process.exit(1); }

  // Read ghost.md — parse only first YAML frontmatter block
  const ghostMd = fs.readFileSync(path.join(POST_DIR, 'ghost.md'), 'utf-8');
  const lines = ghostMd.split('\n');

  let firstFm = -1, secondFm = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim() === '---') {
      if (firstFm === -1) firstFm = i;
      else if (secondFm === -1) { secondFm = i; break; }
    }
  }

  let fm = {};
  if (firstFm !== -1 && secondFm !== -1) {
    for (let i = firstFm + 1; i < secondFm; i++) {
      const line = lines[i];
      const idx = line.indexOf(':');
      if (idx > 0) fm[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
  }

  const bodyLines = secondFm !== -1 ? lines.slice(secondFm + 1) : lines;
  const title = fm.title || '第十七篇';
  const slug = fm.slug || 'neijing-yin-zhong-you-yin';
  const tags = (fm.tags || '').split(',').map(s => s.trim()).filter(Boolean);
  const excerpt = fm.excerpt || '';

  console.log(`📖 Title: ${title}`);
  console.log(`📖 Slug: ${slug}`);
  console.log(`📖 Body: ${bodyLines.length} lines`);

  // Upload images
  console.log('\n📤 Uploading images...');
  const images = ['cover.jpg','card-01.jpg','card-02.jpg','card-03.jpg','card-04.jpg','card-05.jpg','card-06.jpg','card-07.jpg','card-08.jpg','feature-wide.jpg'];
  const urlMap = {};
  for (const name of images) {
    const fp = path.join(IMG_DIR, name);
    if (!fs.existsSync(fp)) { console.log(`  ⚠️  ${name} not found`); continue; }
    try {
      const result = await uploadImage(fp);
      if (result.images && result.images[0] && result.images[0].url) {
        urlMap[name] = result.images[0].url;
        console.log(`  ✅ ${name}`);
      } else { console.log(`  ⚠️  ${name}: no url returned`); }
    } catch (e) { console.log(`  ❌ ${name}: ${e.message}`); }
  }
  console.log(`   Total: ${Object.keys(urlMap).length}/9`);

  // Build markdown body with CDN image URLs
  let mdBody = bodyLines.join('\n').trim();
  for (const [name, url] of Object.entries(urlMap)) {
    const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    mdBody = mdBody.replace(new RegExp(`\\(images/${escapedName}\\)`, 'g'), `(${url})`);
  }

  // Lexical document
  const lexical = JSON.stringify({
    root: {
      children: [{ type: 'markdown', version: 1, markdown: mdBody }],
      direction: null, format: '', indent: 0, type: 'root', version: 1
    }
  });

  // HTML fallback
  let html = mdBody;
  html = html.replace(/!\[(.*?)\]\(([^)]+)\)/g, '<figure class="kg-card kg-image-card"><img src="$2" class="kg-image" alt="$1" loading="lazy"/></figure>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>');
  html = html.replace(/^---$/gm, '<hr/>');
  const finalHtml = html.split('\n').map(l => l.trim()).filter(Boolean)
    .map(l => l.startsWith('<') ? l : `<p>${l}</p>`).join('\n');

  console.log(`\n📄 Markdown: ${mdBody.length} chars`);
  console.log(`📄 HTML: ${finalHtml.length} chars`);

  // Create or update
  const existingPost = await new Promise((resolve, reject) => {
    const url = new URL(`/ghost/api/admin/posts/slug/${slug}/`, GHOST_URL);
    const opts = {
      hostname: url.hostname, path: url.pathname + url.search, method: 'GET',
      headers: { 'Authorization': `Ghost ${jwtFromKey(GHOST_KEY)}`, 'Accept-Version': 'v5.73' }
    };
    const req = https.request(opts, res => { let b=''; res.on('data',c=>b+=c); res.on('end',()=>{ try { resolve(JSON.parse(b)); } catch { reject(new Error(b)); }}); });
    req.on('error', reject); req.end();
  });

  if (existingPost.posts && existingPost.posts[0]) {
    const postId = existingPost.posts[0].id;
    console.log(`\n📝 Updating existing draft (id=${postId})...`);
    const result = await apiPut(`/ghost/api/admin/posts/${postId}/`, {
      posts: [{ title, slug, excerpt: excerpt || title, status: 'draft',
        feature_image: urlMap['cover.jpg'] || '', tags: tags.map(t => ({ name: t })),
        lexical, html: finalHtml, updated_at: existingPost.posts[0].updated_at }]
    });
    if (result.posts?.[0]) console.log(`✅ Updated! ${GHOST_URL}/ghost/#/editor/post/${result.posts[0].id}`);
    else console.error('❌', JSON.stringify(result).slice(0, 800));
  } else {
    console.log('\n📝 Creating new Ghost draft...');
    const result = await apiPost('/ghost/api/admin/posts/', {
      posts: [{ title, slug, excerpt: excerpt || title, status: 'draft',
        feature_image: urlMap['cover.jpg'] || '', tags: tags.map(t => ({ name: t })),
        lexical, html: finalHtml }]
    });
    if (result.posts?.[0]) console.log(`✅ Created! ${GHOST_URL}/ghost/#/editor/post/${result.posts[0].id}`);
    else console.error('❌', JSON.stringify(result).slice(0, 800));
  }
}

main().catch(e => console.error('❌', e.message));
