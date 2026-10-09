"""Exact binary PLY triangle reader; accepts comments, singular/plural index labels."""
from pathlib import Path
import numpy as np
def read_ply(path):
 data=Path(path).read_bytes();stop=data.index(b'end_header\n')+len(b'end_header\n');head=data[:stop].decode('ascii').splitlines();lines=[x for x in head if not x.startswith(('comment ','obj_info '))]
 assert lines[0:2]==['ply','format binary_little_endian 1.0'] and lines[3:6]==['property float x','property float y','property float z'] and len(lines)==9,repr(head)
 assert lines[7] in ['property list uchar int vertex_indices','property list uchar int vertex_index'],repr(head)
 nv=int(lines[2].split()[-1]);nf=int(lines[6].split()[-1]);assert len(data)==stop+12*nv+13*nf
 v=np.frombuffer(data,'<f4',nv*3,stop).reshape(-1,3).copy();a=np.frombuffer(data,dtype=[('n','u1'),('f','<i4',(3,))],count=nf,offset=stop+12*nv);assert (a['n']==3).all();f=a['f'].copy()
 assert np.isfinite(v).all() and (not nf or f.min()>=0 and f.max()<nv)
 return v,f,dict(header=head,order_and_winding_preserved=True)
