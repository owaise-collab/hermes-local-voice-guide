"""Download one pinned official GGUF using curl resume, then check SHA256."""
import argparse
import hashlib
from pathlib import Path
import subprocess

REPO = 'InternScience/Agents-A1-4B-Q8_0-GGUF'
REVISION = 'a5d63881e0ca8eee3c0f14663a5fa2a2c55e1b54'
FILENAME = 'Agents-A1-4B-Q8_0.gguf'
SIZE = 4482404032
SHA256 = 'c327f66e820dae550bd230394595071c79f48c88d411b452d013ee4b5999fcea'
URL = f'https://huggingface.co/{REPO}/resolve/{REVISION}/{FILENAME}'


def verified(path):
    if not path.exists() or path.stat().st_size != SIZE:
        return False
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() == SHA256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    target = args.output.expanduser().resolve()
    if verified(target):
        print(f'Already verified: {target}')
        return
    if target.exists():
        raise SystemExit('Destination exists but is not the verified model. Choose another path; it was not overwritten.')
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + '.partial')
    curl = 'curl.exe' if __import__('os').name == 'nt' else 'curl'
    subprocess.run([curl, '--location', '--fail', '--retry', '4', '--connect-timeout', '30',
                    '--continue-at', '-', '--output', str(partial), URL], check=True)
    if not verified(partial):
        raise SystemExit('Checksum mismatch. Keep the final model path unused; remove the partial file and retry.')
    partial.replace(target)
    print(f'Verified: {target}\nSHA256: {SHA256}')


if __name__ == '__main__':
    main()
