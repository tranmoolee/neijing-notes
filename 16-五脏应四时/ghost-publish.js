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
  if (!id || !secret) throw new Error('Invalid GHOST_ADMIN_API_KEY format (should be id:secret)');
  // Node 18+ has crypto; we can use jsonwebtoken library or manual JWT
  // Using a manual approach since jsonwebtoken may not be available
  const jose = require('crypto');
  const base64url = (buf) => buf.toString('base64url');
  const header = { alg: 'HS256', kid: id, typ: 'JWT' };
  const now = Math.floor(Date.now() / 1000);
  const payload = { iat: now, exp: now + 5 * 60, aud: '/admin/' };
  const b64h = base64url(Buffer.from(JSON.stringify(header)));
  const b64p = base64url(Buffer.from(JSON.stringify(payload)));
  const signature = jose.createHmac('sha256', Buffer.from(secret, 'hex')).update(`${b64h}.${b64p}`).digest('base64url');
  return `${b64h}.${b64p}.${signature}`;
}

function apiPost(pathname, body) {
  return new Promise((resolve, reject) => {
    const url = new URL(pathname, GHOST_URL);
    const token = jwtFromKey(GHOST_KEY);
    const data = JSON.stringify(body);
    const opts = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: 'POST',
      headers: {
        'Authorization': `Ghost ${token}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
        'Accept-Version': 'v5.0',
      }
    };
    const req = https.request(opts, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try { resolve(JSON.parse(body)); }
        catch { reject(new Error(body)); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    const token = jwtFromKey(GHOST_KEY);
    const boundary = '----FormBoundary' + Math.random().toString(36).slice(2);
    const fileData = fs.readFileSync(filePath);
    const fileName = path.basename(filePath);
    const header = [
      `--${boundary}`,
      `Content-Disposition: form-data; name="file"; filename="${fileName}"`,
      `Content-Type: image/jpeg`,
      '',
    ].join('\r\n') + '\r\n';
    const footer = '\r\n--' + boundary + '--\r\n';
    const body = Buffer.concat([
      Buffer.from(header, 'utf-8'),
      fileData,
      Buffer.from(footer, 'utf-8'),
    ]);

    const url = new URL('/ghost/api/admin/images/upload/', GHOST_URL);
    const opts = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Authorization': `Ghost ${token}`,
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length,
        'Accept-Version': 'v5.0',
      }
    };
    const req = https.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch { reject(new Error(data)); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

async function main() {
  if (!GHOST_KEY) { console.error('❌ GHOST_ADMIN_API_KEY not set'); process.exit(1); }

  // 1. Upload images
  console.log('📤 Uploading images to Ghost...');
  const images = ['cover.jpg', 'card-01.jpg', 'card-02.jpg', 'card-03.jpg', 'card-04.jpg', 'card-05.jpg', 'card-06.jpg', 'card-07.jpg', 'card-08.jpg'];
  const urlMap = {};
  for (const name of images) {
    const fp = path.join(IMG_DIR, name);
    if (!fs.existsSync(fp)) { console.log(`  ⚠️  ${name} not found`); continue; }
    try {
      const result = await uploadImage(fp);
      if (result.images && result.images[0] && result.images[0].url) {
        urlMap[name] = result.images[0].url;
        console.log(`  ✅ ${name}`);
      } else {
        console.log(`  ⚠️  ${name}: no url in response`, JSON.stringify(result).slice(0,200));
      }
    } catch (e) {
      console.log(`  ❌ ${name}: ${e.message}`);
    }
  }

  // 2. Read ghost.md and build post
  const ghostMd = fs.readFileSync(path.join(POST_DIR, 'ghost.md'), 'utf-8');
  const lines = ghostMd.split('\n');

  // Parse frontmatter
  let fm = {}, bodyLines = [], inFm = false;
  let title = '五脏应四时';
  let slug = 'neijing-wuzang-ying-sishi';
  let tags = ['学渣读内经', '黄帝内经'];
  let excerpt = '';
  let featureImage = '';

  for (const line of lines) {
    if (line.trim() === '---') { inFm = !inFm; continue; }
    if (inFm) {
      if (line.startsWith('title:')) title = line.slice(6).trim().replace(/^"|"$/g, '');
      else if (line.startsWith('slug:')) slug = line.slice(5).trim();
      else if (line.startsWith('tags:')) tags = line.slice(5).trim().split(',').map(s => s.trim());
      else if (line.startsWith('excerpt:')) excerpt = line.slice(8).trim();
      else if (line.startsWith('feature_image:')) featureImage = line.slice(15).trim();
    } else {
      bodyLines.push(line);
    }
  }

  // Build HTML body with image URLs
  const bodyHtml = bodyLines.map(line => {
    const imgMatch = line.match(/!\[.*?\]\((images\/[^)]+)\)/);
    if (imgMatch) {
      const localRef = imgMatch[1];
      const fname = path.basename(localRef);
      const cdnUrl = urlMap[fname];
      if (cdnUrl) {
        return `<figure class="kg-card kg-image-card"><img src="${cdnUrl}" class="kg-image" alt="" loading="lazy"/></figure>`;
      }
      return '';
    }
    if (line.startsWith('> ')) {
      return `<blockquote><p>${line.slice(2)}</p></blockquote>`;
    }
    if (line.startsWith('## ')) {
      return `<h2>${line.slice(3)}</h2>`;
    }
    if (line.startsWith('---')) {
      return '<hr/>';
    }
    if (line.trim() === '') {
      return '';
    }
    // Bold
    let text = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Tables
    if (line.trim().startsWith('|')) {
      return line;
    }
    return `<p>${text}</p>`;
  }).join('\n');

  // Handle tables - simple conversion
  const tablePattern = /\|(.+)\|/g;
  let inTable = false;
  const finalHtml = bodyHtml.split('\n').map(line => {
    if (line.trim().startsWith('|')) {
      const cells = line.split('|').filter(c => c.trim()).map(c => c.trim());
      if (cells.every(c => /^[-:]+$/.test(c.replace(/\s/g, '')))) return ''; // separator row
      const rowHtml = cells.map(c => `<td>${c}</td>`).join('');
      if (!inTable) { inTable = true; return `<table><thead><tr>${rowHtml}</tr></thead><tbody>`; }
      return `<tr>${rowHtml}</tr>`;
    } else {
      if (inTable) { inTable = false; return '</tbody></table>\n' + line; }
      return line;
    }
  }).join('\n') + (inTable ? '</tbody></table>' : '');

  // 3. Create post
  const postData = {
    posts: [{
      title,
      slug,
      excerpt: excerpt || title,
      status: 'draft',
      feature_image: urlMap['cover.jpg'] || '',
      tags: tags.map(t => ({ name: t.trim() })),
      html: finalHtml,
    }]
  };

  console.log('\n📝 Creating Ghost draft...');
  const result = await apiPost('/ghost/api/admin/posts/', postData);
  if (result.posts && result.posts[0]) {
    const p = result.posts[0];
    console.log(`✅ Ghost draft created!`);
    console.log(`   Title: ${p.title}`);
    console.log(`   URL: ${GHOST_URL}/ghost/#/editor/post/${p.id}`);
  } else {
    console.error('❌ Failed:', JSON.stringify(result, null, 2).slice(0, 500));
  }
}

main().catch(e => console.error('❌', e.message));
