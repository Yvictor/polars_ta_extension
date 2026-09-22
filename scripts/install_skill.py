"""Install the portable polars-talib skill without changing agent configuration."""
import argparse
from pathlib import Path
import shutil


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=['codex','claude','cursor','agents'],required=True)
    parser.add_argument('--project',type=Path,help='Project directory; default: personal installation')
    args=parser.parse_args()
    folders={'codex':'.agents','claude':'.claude','cursor':'.cursor','agents':'.agents'}
    base=(args.project or Path.home()).expanduser().resolve()
    destination=base/folders[args.agent]/'skills'/'polars-talib'
    source=Path(__file__).resolve().parents[1]/'skills'/'polars-talib'
    if destination.exists():
        parser.error(f'{destination} already exists; review or remove it before reinstalling')
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source,destination)
    print(f'Installed {destination}. Restart your agent session to discover the skill.')


if __name__=='__main__':main()
