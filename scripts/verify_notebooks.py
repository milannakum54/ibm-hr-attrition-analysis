"""Execute all saved notebooks with the current Python interpreter.

Run from any folder: python scripts/verify_notebooks.py
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import sys
import argparse
import asyncio
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]


def main():
    paths = sorted((ROOT/'notebooks').glob('*.ipynb'))
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notebook',choices=[p.name for p in paths],help='Verify just one notebook')
    args=parser.parse_args()
    if args.notebook:
        paths=[ROOT/'notebooks'/args.notebook]
    # Use an isolated kernelspec so an unrelated global Python is never selected.
    with TemporaryDirectory(prefix='hr-notebook-check-') as temporary:
        directory=Path(temporary)
        kernel=directory/'kernels'/'hr-verification'
        kernel.mkdir(parents=True)
        (kernel/'kernel.json').write_text(json.dumps({
            'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
            'display_name':'HR verification','language':'python'}),encoding='utf-8')
        old=os.environ.get('JUPYTER_PATH')
        os.environ['JUPYTER_PATH']=str(directory)+(os.pathsep+old if old else '')
        try:
            for path in paths:
                notebook=nbformat.read(path,as_version=4)
                nbformat.validate(notebook)
                print(f'Executing {path.name}',flush=True)
                client=NotebookClient(notebook,timeout=180,startup_timeout=60,
                    kernel_name='hr-verification',shutdown_kernel='immediate',
                    resources={'metadata':{'path':str(ROOT/'notebooks')}})
                # ZMQ needs add_reader; Windows' default Proactor loop uses a
                # helper thread that can fail during native handle cleanup.
                loop_factory=asyncio.SelectorEventLoop if sys.platform=='win32' else None
                with asyncio.Runner(loop_factory=loop_factory) as runner:
                    runner.run(client.async_execute())
                nbformat.write(notebook,path)
                print(f'Passed {path.name}',flush=True)
        finally:
            if old is None:
                os.environ.pop('JUPYTER_PATH',None)
            else:
                os.environ['JUPYTER_PATH']=old
    print(f'Verified {len(paths)} notebook(s).',flush=True)


if __name__=='__main__':
    main()
