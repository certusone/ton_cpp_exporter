#!/usr/bin/env python3.6

import subprocess
import argparse
import tempfile
import os
import json
import base64
import binascii
import re

parser = argparse.ArgumentParser()
parser.add_argument('--output', help="node_exporter collector directory", required=True)
parser.add_argument('--engine-console-binary', help="Binary path for validator-engine-console", required=True)
parser.add_argument('--lite-client-binary', help="Binary path for lite-client", required=True)
parser.add_argument('--validator-client-key', help="Validator client key", required=True)
parser.add_argument('--validator-server-pub', help="Validator server pubkey", required=True)
parser.add_argument('--liteserver-pub', help="Lite server pubkey", required=True)
args = parser.parse_args()

LITE_CLIENT = [
    args.lite_client_binary,
    '-a', '127.0.0.1:3031',
    '-p', args.liteserver_pub
]

output = subprocess.check_output([
    args.engine_console_binary,
    '-a', '127.0.0.1:3030',
    '-k', args.validator_client_key,
    '-p', args.validator_server_pub,
    '-c', 'getstats',
    '-c', 'quit'],
    # https://github.com/ton-blockchain/ton/issues/292
    stdin=subprocess.PIPE
)

want = [
    b'unixtime',
    b'masterchainblocktime',
    b'stateserializermasterchainseqno',
    b'shardclientmasterchainseqno',
]

values = {}

for line in output.split(b'\n'):
    parts = line.split(b'\t')
    if parts[0] in want:
        values[parts[0]] = parts[-1]

for k in want:
    values[k]

output = subprocess.check_output(LITE_CLIENT + ['-rc', 'runmethod -1:3333333333333333333333333333333333333333333333333333333333333333 active_election_id'], stdin=subprocess.PIPE)
active_election_id = int(re.findall(rb'result:  \[ (.*) \]', output)[0])

output = subprocess.check_output(LITE_CLIENT + ['-rc', 'allshards'], stdin = subprocess.PIPE)
allshards = re.findall(rb'^shard #(\d+) : \(\d,\d+,(\d+)\)', output, re.M)

with open('/opt/ton/data/db/config.json', 'r') as f:
    cfg = json.load(f)

with tempfile.NamedTemporaryFile(delete=False, dir=args.output) as fp:
    for k, v in values.items():
        fp.write(b'ton_%s %s\n' % (k, v))

    for n, validator in enumerate(cfg['validators']):
        adnl_b64 = next(filter(
            lambda x: x['@type'] == 'engine.validatorAdnlAddress',
            validator['adnl_addrs']))['id']

        adnl_addr = binascii.hexlify(base64.b64decode(adnl_b64))

        fp.write(b'ton_validator_election_date{index="%d", adnl_addr="%s"} %d\n' % (n, adnl_addr, validator['election_date']))
        fp.write(b'ton_validator_expire_at{index="%d", adnl_addr="%s"} %d\n' % (n, adnl_addr, validator['expire_at']))

    fp.write(b'ton_election_active_id %d\n' % active_election_id)

    for id_, height in allshards:
        fp.write(b'ton_shard_height{shard_id="%s"} %s\n' % (id_, height))

    fp.write(b'\n')
    fp.flush()
    os.fchmod(fp.fileno(), 0o644)
    fp.close()
    os.rename(fp.name, os.path.join(args.output, 'ton.prom'))
