"""Physical input snapshots, written only during preflight, never timed children."""
import hashlib
from pathlib import Path
import re


def digest_frame(data):
    digest=hashlib.sha256(str(data.schema).encode())
    for column in data:
        if column.null_count():
            raise ValueError('the fixed timing fixture must have no nulls')
        digest.update(column.name.encode());digest.update(column.to_numpy().tobytes())
    return digest.hexdigest()


def file_digest(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):digest.update(block)
    return digest.hexdigest()


def preserve(data,folder,expected):
    import polars as pl
    if digest_frame(data)!=expected:raise ValueError('fixture digest changed before snapshot')
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    path=folder/(expected+'.arrow')
    if not path.exists():data.write_ipc(path,compression='zstd')
    stored=pl.read_ipc(path,memory_map=False)
    if digest_frame(stored)!=expected or str(stored.schema)!=str(data.schema):
        raise ValueError('retained fixture does not reproduce physical input bytes/schema')
    return {'file':path.name,'sha256':file_digest(path),'bytes':path.stat().st_size,
            'fixture_sha256':expected,'schema':str(data.schema),'rows':data.height}


def validate(folder,records,expected):
    import polars as pl
    if set(records)!=set(expected):raise ValueError('raw input case inventory differs')
    paths=set()
    for case,record in records.items():
        key=expected[case];name=record['file']
        if not re.fullmatch('[0-9a-f]{64}\\.arrow',name) or name!=key+'.arrow':
            raise ValueError('raw input path is not the bound fixture digest')
        path=Path(folder)/name;paths.add(name)
        if (path.is_symlink() or not path.is_file() or type(record['bytes'])is not int
                or path.stat().st_size!=record['bytes'] or file_digest(path)!=record['sha256']
                or record['fixture_sha256']!=key):
            raise ValueError('raw input file bytes or identity changed')
        data=pl.read_ipc(path,memory_map=False)
        if (str(data.schema)!=record['schema'] or data.height!=record['rows']
                or digest_frame(data)!=key):
            raise ValueError('raw input schema or physical arrays differ')
    if len(paths)!=len(set(expected.values())):raise ValueError('raw input deduplication differs')
    return len(paths)
