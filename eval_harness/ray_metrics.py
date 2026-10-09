"""Unchanged pure functions selected from existing research code. No paths or labels."""
import numpy as np
DT=np.dtype([('face','<i4'),('t','<f8'),('point','<f8',(3,))])

def hits(path):return np.fromfile(path,DT,offset=8)


def normals(v,f,ids):
 t=v[f[ids]].astype(np.float64);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(n,axis=1)
 with np.errstate(divide='ignore',invalid='ignore'):n/=length[:,None]
 return n


def errors(src,cur,sv,sf,v,f):
 visible=src['face']>=0;good=visible&(cur['face']>=0);n=np.full(len(src),np.inf);d=np.full(len(src),np.inf)
 sn=normals(sv,sf,src['face'][good]);cn=normals(v,f,cur['face'][good]);n[good]=np.degrees(np.arccos(np.clip(np.sum(sn*cn,axis=1),-1,1)));n[~np.isfinite(n)]=np.inf;d[good]=np.abs(src['t'][good]-cur['t'][good])
 return n,d,visible


