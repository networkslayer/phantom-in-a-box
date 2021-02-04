#!/usr/bin/env python
#
# usage:
#        conv2vmx-ovf.py some-vm.ovf
#
# ref: http://www.cnblogs.com/eshizhan/p/3332020.html
#

import hashlib
import re
import sys
import os
fn = sys.argv[1]
fp = open(fn).read()
if hasattr(fp,'decode'): 
    fp = fp.decode('utf-8')

# Replace Hardware Lines for VMWare Import
print('INFO: Fixing OVF file: {}'.format(fn))
fp = fp.replace('<OperatingSystemSection ovf:id="80">', '<OperatingSystemSection ovf:id="101">')
fp = fp.replace('<vssd:VirtualSystemType>virtualbox-2.2', '<vssd:VirtualSystemType>vmx-7')
fp = fp.replace('<rasd:Caption>sataController', '<rasd:Caption>scsiController')
fp = fp.replace('<rasd:Description>SATA Controller', '<rasd:Description>SCSI Controller')
fp = fp.replace('<rasd:ElementName>sataController', '<rasd:ElementName>scsiController')
fp = fp.replace('<rasd:ResourceSubType>AHCI', '<rasd:ResourceSubType>lsilogic')
fp = fp.replace('<rasd:ResourceType>20', '<rasd:ResourceType>6')

end = fp.find('<rasd:Caption>sound')
start = fp.rfind('<Item>', 0, end)
fp = fp[:start] + '<Item ovf:required="false">' + fp[start+len('<Item>'):]

nfp = open(fn, 'wb')
nfp.write(fp.encode('utf8'))
nfp.close()

# Create Vars for File Names of Interest

dir, file = os.path.split(fn)
pos = re.split('.ovf',file)
full_vmdk_file = dir + '/' + pos[0] + '-disk001.vmdk'
full_mf_file = dir + '/' + pos[0] + '.mf'
vmdk_file = pos[0] + '-disk001.vmdk'
ovf_file = file

# Fix the Manifest file - By recalculating SHA1 Hash
try:
    print('INFO: Calculating new SHA1 Hash for: {}'.format(fn))
    sha1_hash_ovf = hashlib.sha1()
    with open(fn, "rb") as f:
        # read and update hash string in 4k chunks
        for byte_block in iter(lambda: f.read(4096),b""):
            sha1_hash_ovf.update(byte_block)
        print(sha1_hash_ovf.hexdigest())
    f.close()
except:
    print('ERROR: Unable to calculate new hash for {}\n'.format(fn))
    exit(1)

try:
    print('INFO: Calculating new SHA1 Hash for: {}'.format(full_vmdk_file))
    sha1_hash_vmdk = hashlib.sha1()
    with open(full_vmdk_file, "rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha1_hash_vmdk.update(byte_block)
        print(sha1_hash_vmdk.hexdigest())
    f.close()
except:
    print('ERROR: Unable to calculate hash for {}\n'.format(full_vmdk_file))
    exit(1)


# Fix Manifest File
try:
    print('INFO: : OverWriting Manifest: {}\n'.format(full_mf_file))
    with open(full_mf_file, 'w') as manifest:
        manifest.write(str('SHA1 ({}) = {}\n').format(vmdk_file, sha1_hash_vmdk.hexdigest()))
        manifest.write(str('SHA1 ({}) = {}\n').format(ovf_file, sha1_hash_ovf.hexdigest()))
    manifest.close()
except:
    print('ERROR: Unable to write manifest file: {}\n'.format(full_mf_file))
    exit(1)
    

print('Success!')
