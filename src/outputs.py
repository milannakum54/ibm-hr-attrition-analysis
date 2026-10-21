"""Stage generated files so calculation failures preserve previous results."""
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


@contextmanager
def staged_outputs(output_root, input_path):
    root = Path(output_root).resolve()
    source = Path(input_path).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix='.analysis-', dir=root) as temporary:
        stage = Path(temporary)
        yield stage
        files = sorted(p for p in stage.rglob('*') if p.is_file())
        targets = [(p,root/p.relative_to(stage)) for p in files]
        # Preflight every target before replacing any existing result.
        for _,target in targets:
            if target.resolve() == source:
                raise ValueError('Output would overwrite the input CSV; choose another --output-dir.')
            if target.exists() and not target.is_file():
                raise ValueError(f'Output path is a directory instead of a file: {target}')
            target.parent.mkdir(parents=True, exist_ok=True)
        # Manifest is published last; it describes the completed generation.
        targets.sort(key=lambda pair: pair[1].name == 'run_manifest.json')
        for path,target in targets:
            path.replace(target)
