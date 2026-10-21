"""Real CLI runs, output integrity and failure isolation."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import pandas as pd
import pytest
from PIL import Image
import run_analysis
import run_milan
from src.plots import numeric_plots
from src.categorical import categorical_plots
from src.outputs import staged_outputs

ROOT=Path(__file__).resolve().parents[1]

def digest_tree(path):
    return {str(p.relative_to(path)):hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}

def command(script,*args,cwd):
    return subprocess.run([sys.executable,str(ROOT/script),*map(str,args)],cwd=cwd,capture_output=True,text=True,timeout=180)

def test_full_cli_model_rerun_and_stale_output_cleanup(raw_path,tmp_path):
    out=tmp_path/'results with spaces'
    original=raw_path.read_bytes()
    result=command('run_analysis.py','--data',raw_path,'--output-dir',out,'--model',cwd=tmp_path)
    assert result.returncode==0,result.stderr
    assert raw_path.read_bytes()==original
    figures=list((out/'visualizations').glob('*.png'))
    assert len(figures)==12
    for path in figures:
        with Image.open(path) as image:
            assert min(image.size)>100
            image.verify()
    manifest=json.loads((out/'reports/run_manifest.json').read_text())
    assert manifest['model_included'] and manifest['testable_comparisons']==16
    statistics=pd.read_csv(out/'reports/statistical_tests.csv')
    assert manifest['total_comparisons']==len(statistics)==16
    assert manifest['testable_comparisons']==int(statistics.status.eq('ok').sum())
    assert 'Testable comparisons: 16/16.' in (out/'reports/results.md').read_text()
    assert len(manifest['figures'])==12
    metrics=pd.read_csv(out/'reports/model_metrics.csv'); assert len(metrics)==2
    first=digest_tree(out)
    result=command('run_analysis.py','--data',raw_path,'--output-dir',out,'--model',cwd=tmp_path)
    assert result.returncode==0,result.stderr
    assert digest_tree(out)==first
    result=command('run_analysis.py','--data',raw_path,'--output-dir',out,cwd=tmp_path)
    assert result.returncode==0,result.stderr
    assert not (out/'reports/model_metrics.csv').exists()
    assert not json.loads((out/'reports/run_manifest.json').read_text())['model_included']

@pytest.mark.parametrize('script',['run_analysis.py','run_milan.py'])
def test_cli_missing_file_returns_clear_error_and_preserves_outputs(tmp_path,script):
    out=tmp_path/'out'; out.mkdir(); (out/'existing.txt').write_text('keep')
    result=command(script,'--data',tmp_path/'missing.csv','--output-dir',out,cwd=tmp_path)
    assert result.returncode==2
    assert 'Analysis could not complete' in result.stderr
    assert 'Traceback' not in result.stderr
    assert digest_tree(out)=={'existing.txt':hashlib.sha256(b'keep').hexdigest()}

def test_full_analysis_supports_single_record_without_model(raw_frame,tmp_path):
    path=tmp_path/'single.csv'; raw_frame.head(1).to_csv(path,index=False)
    out=tmp_path/'one'
    run_analysis.run(path,out)
    tests=pd.read_csv(out/'reports/statistical_tests.csv')
    assert (tests.status=='not_testable').all()
    manifest=json.loads((out/'reports/run_manifest.json').read_text())
    assert manifest['total_comparisons']==len(tests)==16
    assert manifest['testable_comparisons']==0
    text=(out/'reports/results.md').read_text()
    assert 'Testable comparisons: 0/16.' in text
    assert 'unavailable' in text and 'nan' not in text.lower()
    assert len(list((out/'visualizations').glob('*.png')))==12

def test_model_failure_preserves_existing_results(raw_frame,tmp_path):
    path=tmp_path/'single.csv'; raw_frame.head(1).to_csv(path,index=False)
    out=tmp_path/'out'; out.mkdir(); (out/'keep.txt').write_text('old results')
    before=digest_tree(out)
    with pytest.raises(ValueError,match='both attrition classes'):
        run_analysis.run(path,out,True)
    assert digest_tree(out)==before

def test_numeric_plot_ownership(prepared,tmp_path):
    (tmp_path/'01_attrition_distribution.png').write_bytes(b'keep')
    paths=numeric_plots(prepared,tmp_path)
    assert {p.name[:2] for p in paths}=={'05','08','09','11','12'}
    assert (tmp_path/'01_attrition_distribution.png').read_bytes()==b'keep'

@pytest.mark.parametrize('function',[numeric_plots,categorical_plots])
def test_empty_plot_input_rejected_before_writing(prepared,tmp_path,function):
    with pytest.raises(ValueError,match='empty'): function(prepared.head(0),tmp_path)
    assert list(tmp_path.iterdir())==[]

def test_staging_preserves_previous_results_on_failure(tmp_path):
    out=tmp_path/'out'; out.mkdir(); existing=out/'report.txt'; existing.write_text('old')
    with pytest.raises(RuntimeError):
        with staged_outputs(out,tmp_path/'input.csv') as stage:
            (stage/'report.txt').write_text('new')
            raise RuntimeError('Simulated calculation failure')
    assert existing.read_text()=='old'
    assert list(out.iterdir())==[existing]

def test_staging_prevents_input_overwrite(tmp_path):
    source=tmp_path/'raw.csv'; source.write_text('source bytes')
    with pytest.raises(ValueError,match='overwrite'):
        with staged_outputs(tmp_path,source) as stage:
            (stage/'raw.csv').write_text('replacement')
    assert source.read_text()=='source bytes'

def test_cleanup_cannot_delete_input(raw_frame,tmp_path):
    reports=tmp_path/'reports'; reports.mkdir()
    source=reports/'model_metrics.csv'; raw_frame.head(10).to_csv(source,index=False)
    before=source.read_bytes()
    with pytest.raises(ValueError,match='overwrite'): run_analysis.run(source,tmp_path)
    assert source.read_bytes()==before

def test_milan_plot_failure_preserves_outputs(raw_path,tmp_path,monkeypatch):
    out=tmp_path/'out'; out.mkdir(); (out/'keep.txt').write_text('old')
    def broken(*args,**kwargs): raise RuntimeError('Simulated plotting failure')
    monkeypatch.setattr(run_milan,'categorical_plots',broken)
    before=digest_tree(out)
    with pytest.raises(RuntimeError): run_milan.run(raw_path,out)
    assert digest_tree(out)==before

def test_output_file_collision_preflight_preserves_previous_outputs(tmp_path):
    (tmp_path/'b.txt').mkdir(); (tmp_path/'a.txt').write_text('old')
    with pytest.raises(ValueError,match='directory'):
        with staged_outputs(tmp_path,tmp_path/'input.csv') as stage:
            (stage/'a.txt').write_text('new'); (stage/'b.txt').write_text('new')
    assert (tmp_path/'a.txt').read_text()=='old'

@pytest.mark.parametrize('module_name',['src.plots','src.categorical'])
def test_failed_image_save_closes_figure(tmp_path,monkeypatch,module_name):
    import importlib
    import matplotlib.pyplot as plt
    module=importlib.import_module(module_name)
    fig,_=plt.subplots()
    def failure(*args,**kwargs): raise PermissionError('Simulated permission failure')
    monkeypatch.setattr(fig,'savefig',failure)
    with pytest.raises(PermissionError): module.save(fig,tmp_path,'figure')
    assert not plt.fignum_exists(fig.number)

def test_output_root_is_file_returns_clear_cli_error(raw_path,tmp_path):
    out=tmp_path/'file.txt'; out.write_text('keep')
    result=command('run_analysis.py','--data',raw_path,'--output-dir',out,cwd=tmp_path)
    assert result.returncode==2 and 'Traceback' not in result.stderr
    assert out.read_text()=='keep'
