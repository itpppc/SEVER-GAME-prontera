#!/usr/bin/env python3
"""Build the ศึกลงกา Android app (a WebView around https://sever-game-prontera.vercel.app/rpg) without the Android SDK.

Only needs a JDK and three jars from Maven Central (see JARS below). The binary AndroidManifest.xml and
resources.arsc are written by hand here, since aapt2 is not available from Maven Central.

    python3 tools/android-apk/build_apk.py --keystore lanka.p12 --password ... --out website/downloads/SuekLanka.apk

The keystore must stay the same for every release, or Android refuses to install the update over the old app.
"""
import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = 'th.prontera.lanka'
LABEL = 'ศึกลงกา'
VERSION_CODE = 1
VERSION_NAME = '1.0'
MIN_SDK, TARGET_SDK = 24, 34  # Android 7+; v2-only signing needs 24
MAVEN = 'https://repo1.maven.org/maven2/'
JARS = {  # path on Maven Central -> sha1
    'com/google/android/android/4.1.1.4/android-4.1.1.4.jar': '3fb039385e71e9aa2ba547ea9ea8caa34a4ffac7',
    'com/jakewharton/android/repackaged/dalvik-dx/16.0.1/dalvik-dx-16.0.1.jar': '71ac16d1f34143d86440fca923422f9c2e2ac403',
    'com/android/tools/build/apksig/2.3.0/apksig-2.3.0.jar': '6ef7a58375aa68fb492b58edd97607bee8ee5c5c',
}
ICON_ID = 0x7F010000  # package 0x7f, type 1 (drawable), entry 0
ICON_PATH = 'res/drawable/icon.png'

# --- binary XML ---------------------------------------------------------------------------------

ANDROID_NS = 'http://schemas.android.com/apk/res/android'
ATTR_IDS = {
    'theme': 0x01010000, 'label': 0x01010001, 'icon': 0x01010002, 'name': 0x01010003,
    'exported': 0x01010010, 'screenOrientation': 0x0101001E, 'configChanges': 0x0101001F,
    'minSdkVersion': 0x0101020C, 'versionCode': 0x0101021B, 'versionName': 0x0101021C,
    'targetSdkVersion': 0x01010270, 'allowBackup': 0x01010280, 'hardwareAccelerated': 0x010102D3,
}
T_REF, T_STRING, T_DEC, T_HEX, T_BOOL = 0x01, 0x03, 0x10, 0x11, 0x12
NO_INDEX = 0xFFFFFFFF


def a(name, typ, value, ns=True):
    return (ns, name, typ, value)


MANIFEST = (
    'manifest', [a('versionCode', T_DEC, VERSION_CODE), a('versionName', T_STRING, VERSION_NAME),
                 a('package', T_STRING, PACKAGE, ns=False)], [
        ('uses-sdk', [a('minSdkVersion', T_DEC, MIN_SDK), a('targetSdkVersion', T_DEC, TARGET_SDK)], []),
        ('uses-permission', [a('name', T_STRING, 'android.permission.INTERNET')], []),
        ('application', [a('label', T_STRING, LABEL), a('icon', T_REF, ICON_ID), a('allowBackup', T_BOOL, False),
                         a('hardwareAccelerated', T_BOOL, True)], [
            ('activity', [a('name', T_STRING, PACKAGE + '.MainActivity'), a('exported', T_BOOL, True),
                          a('screenOrientation', T_DEC, 1),  # portrait
                          a('configChanges', T_HEX, 0x04A0)], [  # orientation|keyboardHidden|screenSize
                ('intent-filter', [], [
                    ('action', [a('name', T_STRING, 'android.intent.action.MAIN')], []),
                    ('category', [a('name', T_STRING, 'android.intent.category.LAUNCHER')], []),
                ]),
            ]),
        ]),
    ])


def chunk(typ, header, body):
    """ResChunk_header + rest of header + body; header excludes the 8-byte common header."""
    return struct.pack('<HHI', typ, 8 + len(header), 8 + len(header) + len(body)) + header + body


def string_pool(strings, utf8):
    offsets, data = [], b''
    for s in strings:
        offsets.append(len(data))
        if utf8:
            raw = s.encode('utf-8')
            assert len(s) < 128 and len(raw) < 128, 'long strings not supported'
            data += bytes([len(s), len(raw)]) + raw + b'\0'
        else:
            raw = s.encode('utf-16-le')
            assert len(raw) // 2 < 0x8000
            data += struct.pack('<H', len(raw) // 2) + raw + b'\0\0'
    data += b'\0' * (-len(data) % 4)
    flags = 0x100 if utf8 else 0
    strings_start = 28 + 4 * len(strings)
    header = struct.pack('<IIIII', len(strings), 0, flags, strings_start, 0)
    return chunk(0x0001, header, b''.join(struct.pack('<I', o) for o in offsets) + data)


def build_axml(root):
    # Attribute names with resource ids must come first, in the same order as the resource map.
    attr_names = []

    def collect(node):
        for ns, name, _, _ in node[1]:
            if ns and name not in attr_names:
                attr_names.append(name)
        for c in node[2]:
            collect(c)
    collect(root)
    strings = list(attr_names)

    def idx(s):
        if s not in strings:
            strings.append(s)
        return strings.index(s)

    idx('android')
    idx(ANDROID_NS)
    body = []

    def emit(node, line=[1]):
        tag, attrs, children = node
        ordered = sorted(attrs, key=lambda x: ATTR_IDS[x[1]] if x[0] else 0)  # framework parser expects id order
        packed = b''
        for ns, name, typ, value in ordered:
            raw = NO_INDEX
            if typ == T_STRING:
                raw = data = idx(value)
            elif typ == T_BOOL:
                data = 0xFFFFFFFF if value else 0
            else:
                data = value
            packed += struct.pack('<IIIHBBI', idx(ANDROID_NS) if ns else NO_INDEX, idx(name), raw, 8, 0, typ, data)
        ext = struct.pack('<IIHHHHHH', NO_INDEX, idx(tag), 20, 20, len(ordered), 0, 0, 0)
        body.append(chunk(0x0102, struct.pack('<II', line[0], NO_INDEX), ext + packed))
        line[0] += 1
        for c in children:
            emit(c)
        body.append(chunk(0x0103, struct.pack('<II', line[0], NO_INDEX), struct.pack('<II', NO_INDEX, idx(tag))))
        line[0] += 1

    ns_ext = struct.pack('<II', idx('android'), idx(ANDROID_NS))
    emit(root)
    start_ns = chunk(0x0100, struct.pack('<II', 1, NO_INDEX), ns_ext)
    end_ns = chunk(0x0101, struct.pack('<II', 1, NO_INDEX), ns_ext)
    res_map = chunk(0x0180, b'', b''.join(struct.pack('<I', ATTR_IDS[n]) for n in attr_names))
    inner = string_pool(strings, utf8=False) + res_map + start_ns + b''.join(body) + end_ns
    return chunk(0x0003, b'', inner)


# --- resources.arsc: one drawable "icon" -> res/drawable/icon.png --------------------------------

def build_arsc():
    values = string_pool([ICON_PATH], utf8=True)
    type_strings = string_pool(['drawable'], utf8=False)
    key_strings = string_pool(['icon'], utf8=False)
    spec = chunk(0x0202, struct.pack('<BBHI', 1, 0, 0, 1), struct.pack('<I', 0))
    config = struct.pack('<I', 64) + b'\0' * 60  # default configuration
    entries = struct.pack('<HHI', 8, 0, 0) + struct.pack('<HBBI', 8, 0, T_STRING, 0)
    type_header = struct.pack('<BBHII', 1, 0, 0, 1, 20 + len(config) + 4) + config
    rtype = chunk(0x0201, type_header, struct.pack('<I', 0) + entries)
    name = PACKAGE.encode('utf-16-le').ljust(256, b'\0')
    pkg_header_len = 288
    type_off = pkg_header_len
    key_off = type_off + len(type_strings)
    pkg_header = struct.pack('<I', 0x7F) + name + struct.pack('<IIIII', type_off, 1, key_off, 1, 0)
    pkg = chunk(0x0200, pkg_header, type_strings + key_strings + spec + rtype)
    return chunk(0x0002, struct.pack('<I', 1), values + pkg)


# --- build ----------------------------------------------------------------------------------------

def fetch_jars(cache):
    os.makedirs(cache, exist_ok=True)
    paths = []
    for rel, sha in JARS.items():
        dest = os.path.join(cache, os.path.basename(rel))
        if not os.path.exists(dest):
            urllib.request.urlretrieve(MAVEN + rel, dest)
        if hashlib.sha1(open(dest, 'rb').read()).hexdigest() != sha:
            os.remove(dest)
            sys.exit('checksum mismatch for ' + rel)
        paths.append(dest)
    return paths


# apksig 2.3.0 (newest on Maven Central) touches JDK internals while loading, even with v1 signing off.
EXPORTS = ['--add-exports=java.base/' + p + '=ALL-UNNAMED' for p in ('sun.security.x509', 'sun.security.pkcs', 'sun.security.util')]


def run(*cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--keystore', required=True, help='PKCS12 keystore; created on first run if missing')
    ap.add_argument('--password', required=True)
    ap.add_argument('--alias', default='lanka')
    ap.add_argument('--icon', default=os.path.join(HERE, 'icon-192.png'))
    ap.add_argument('--out', required=True)
    ap.add_argument('--cache', default=os.path.join(tempfile.gettempdir(), 'lanka-apk-jars'))
    o = ap.parse_args()

    android_jar, dx_jar, apksig_jar = fetch_jars(o.cache)
    if not os.path.exists(o.keystore):
        run('keytool', '-genkeypair', '-storetype', 'PKCS12', '-keystore', o.keystore, '-alias', o.alias,
            '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', '-storepass', o.password,
            '-dname', 'CN=Prontera Ramakien, O=TON, C=TH')

    with tempfile.TemporaryDirectory() as tmp:
        classes = os.path.join(tmp, 'classes')
        src = os.path.join(HERE, 'src', 'th', 'prontera', 'lanka', 'MainActivity.java')
        run('javac', '--release', '8', '-nowarn', '-Xlint:-options', '-cp', android_jar, '-d', classes, src)
        dex = os.path.join(tmp, 'classes.dex')
        run('java', '-cp', dx_jar, 'com.android.dx.command.Main', '--dex', '--min-sdk-version=' + str(MIN_SDK),
            '--output=' + dex, classes)

        unsigned = os.path.join(tmp, 'unsigned.apk')
        with zipfile.ZipFile(unsigned, 'w') as z:
            z.writestr(zipfile.ZipInfo('AndroidManifest.xml'), build_axml(MANIFEST), zipfile.ZIP_DEFLATED)
            z.write(dex, 'classes.dex', zipfile.ZIP_DEFLATED)
            # resources.arsc must be stored uncompressed and 4-byte aligned for targetSdk 30+.
            info = zipfile.ZipInfo('resources.arsc')
            info.compress_type = zipfile.ZIP_STORED
            arsc = build_arsc()
            header_len = 30 + len(info.filename)
            pad = -(z.fp.tell() + header_len) % 4
            info.extra = b'\0' * pad
            z.writestr(info, arsc)
            z.write(o.icon, ICON_PATH, zipfile.ZIP_STORED)

        signer = os.path.join(tmp, 'signer')
        run('javac', '-nowarn', '-cp', apksig_jar, '-d', signer, os.path.join(HERE, 'src', 'Sign.java'))
        os.makedirs(os.path.dirname(os.path.abspath(o.out)), exist_ok=True)
        run('java', *EXPORTS, '-cp', signer + os.pathsep + apksig_jar, 'Sign', unsigned, o.out, o.keystore, o.alias, o.password)
    print('built', o.out, os.path.getsize(o.out), 'bytes')


if __name__ == '__main__':
    main()
