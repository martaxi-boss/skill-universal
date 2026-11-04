#!/usr/bin/env python3
"""Ferrari-private Hopper 6.6.1 official demo install; no global APT and no license bypass.
Only run on the owner's Ubuntu VPS. The third-party binary is NOT committed to GitHub.
Checks official feed SHA-1, package PGP signature and ELF SHA-256 before atomic placement.
"""
import base64,hashlib,json,os,re,shutil,subprocess,tempfile,urllib.request
from pathlib import Path
ROOT=Path('/srv/projects/skill-universal')
TOOLS=ROOT/'tools'
FP='7C2D73BAFAF5B9A710A69DA1A26DF815099B1BCD'
def get(url,limit):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=40) as r:
  assert r.status==200 and r.url.startswith('https://www.hopperapp.com/'),'official HTTPS source required'
  b=r.read(limit+1)
 assert 0<len(b)<=limit,'invalid download length'
 return b
out={'action':'private_hopper_demo_install','project':'skill-universal','global_package_unchanged':True}
stage=None
try:
 assert ROOT.is_dir() and not ROOT.is_symlink() and TOOLS.is_dir() and not TOOLS.is_symlink()
 assert os.access(TOOLS,os.W_OK),'Ferrari tools not writable'
 feed=json.loads(get('https://www.hopperapp.com/include/files-api.php?request=releases&public=true',400000))
 row=feed['Ubuntu / Mint']
 version=str(row['version'])
 assert version=='6.6.1','unexpected vendor release'
 assert row.get('publicKeyFingerprint','').upper()==FP,'publisher fingerprint unexpected'
 assert str(row.get('public'))=='1' and str(row.get('beta'))=='0'
 name='Hopper-'+version+'-Linux-demo.deb'
 assert name in str(row['filename'])
 dest=TOOLS/('hopper-'+version)
 exe=dest/'opt/hopper/bin/Hopper'
 if dest.exists() or dest.is_symlink():
  assert exe.is_file() and hashlib.sha256(exe.read_bytes()).hexdigest()==row['main_exe_hash'],'existing Hopper invalid'
  out.update({'status':'already_installed','version':version,'launcher':str(exe)})
 else:
  stage=Path(tempfile.mkdtemp(prefix='.hopper-authenticated-',dir=TOOLS))
  pkg=stage/name
  body=get('https://www.hopperapp.com/downloader/public/'+name,90000000)
  assert len(body)==int(row['file_length']) and hashlib.sha1(body).hexdigest()==row['file_hash'],'package mismatches signed vendor feed'
  pkg.write_bytes(body)
  del body
  sig=stage/'release.sig'
  sig.write_bytes(base64.b64decode(row['signature'],validate=True))
  key=stage/'publisher.asc'
  key.write_bytes(get('https://www.hopperapp.com/hopper-public-key.asc',200000))
  home=stage/'gnupg'
  home.mkdir(mode=0o700)
  a=subprocess.run(['gpg','--homedir',str(home),'--batch','--import',str(key)],capture_output=True,text=True,timeout=25)
  assert a.returncode==0,'publisher key import failed'
  a=subprocess.run(['gpg','--homedir',str(home),'--with-colons','--list-keys'],capture_output=True,text=True,timeout=20)
  assert a.returncode==0 and FP in a.stdout.upper(),'publisher key identity mismatch'
  a=subprocess.run(['gpg','--homedir',str(home),'--batch','--status-fd','1','--verify',str(sig),str(pkg)],capture_output=True,text=True,timeout=25)
  assert a.returncode==0 and any(FP in l.upper() for l in a.stdout.splitlines() if l.startswith('[GNUPG:] VALIDSIG ')),'official package PGP signature failed'
  extracted=stage/'payload'
  extracted.mkdir()
  a=subprocess.run(['/usr/bin/dpkg-deb','-x',str(pkg),str(extracted)],capture_output=True,text=True,timeout=90)
  assert a.returncode==0,'official package could not be extracted'
  launch=extracted/'opt/hopper/bin/Hopper'
  assert launch.is_file() and not launch.is_symlink() and os.access(launch,os.X_OK),'vendor launcher missing'
  assert hashlib.sha256(launch.read_bytes()).hexdigest()==row['main_exe_hash'],'launcher hash mismatch'
  for x in extracted.rglob('*'):
   if x.is_symlink(): assert x.resolve(strict=False).is_relative_to(extracted.resolve()),'external symlink in package'
  source=extracted/'private-provenance'
  source.mkdir()
  shutil.move(str(pkg),source/name)
  shutil.copy2(sig,source/'release.sig')
  shutil.copy2(key,source/'publisher.asc')
  (source/'manifest.json').write_text(json.dumps({'version':version,'publisher_fingerprint':FP,'package_sha1':row['file_hash'],'launcher_sha256':row['main_exe_hash'],'license':'official demo, not activated commercial license'},indent=2))
  extracted.rename(dest)
  out.update({'status':'installed_private','version':version,'launcher':str(exe),'signed_package_verified':True,'paid_license_activated':False})
 a=subprocess.run(['ldd',str(exe)],capture_output=True,text=True,timeout=20)
 out['ldd_missing']=[l.strip()[:140] for l in a.stdout.splitlines() if 'not found' in l][:30]
 out['ldd_exit']=a.returncode
except Exception as e:
 out.update({'status':'failed','reason':type(e).__name__+':'+str(e)[:220]})
finally:
 if stage is not None:shutil.rmtree(stage,ignore_errors=True)
print(json.dumps(out,separators=(',',':')))

if out.get('status')=='failed':
 raise SystemExit(1)
