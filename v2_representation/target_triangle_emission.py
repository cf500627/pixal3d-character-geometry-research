"""Vectorized full Oracle triangle emission; original fixed FP32 diagonal math.

Source sign changes templates at construction, before faces exist. No mesh
traversal, winding repair, coordinate fitting, cleaning, or training occurs.
"""
import numpy as np
import pinned_rounding_reference as rounding

PATTERNS=np.array(((0,1,2,0,2,3),(0,1,3,3,1,2)),dtype=np.int32)

def emit(vertices,base_quads,signs=None):
    v=np.asarray(vertices)
    q=np.asarray(base_quads,dtype=np.int32)
    if v.dtype!=np.float32 or not np.isfinite(v).all() or q.ndim!=2 or q.shape[1]!=4:
        raise ValueError('Finite original FP32 vertices and four support indices required')
    if len(q)==0 or not ((q>=0)&(q<len(v))).all():
        raise ValueError('Nonempty legal support quads required')
    orient=np.full(len(q),-1,np.int8) if signs is None else np.asarray(signs,np.int8)
    if orient.shape!=(len(q),) or not np.isin(orient,[-1,1]).all():
        raise ValueError('Each emitted event requires an explicitly assigned sign')
    scores=[]
    for template in PATTERNS:
        t=q[:,template]
        n0=rounding.cross_fp32(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]])
        n1=rounding.cross_fp32(v[t[:,4]]-v[t[:,3]],v[t[:,5]]-v[t[:,3]])
        scores.append(rounding.align_fp32(n0,n1)[:,0])
    choice=np.where(scores[0]>scores[1],0,1).astype(np.uint8)
    template=PATTERNS[choice].reshape(-1,2,3).copy()
    template[orient>0]=template[orient>0][:,:,[0,2,1]]
    faces=np.take_along_axis(q[:,None,:],template,axis=2).reshape(-1,3)
    oriented_quads=q.copy()
    oriented_quads[orient>0]=oriented_quads[orient>0][:,[0,3,2,1]]
    arrays={'base_quads':q,'score0':scores[0],'score1':scores[1],
            'chosen_pattern':choice,'emitted_orientation':orient}
    detail={'DIAGONAL_FIX_INCLUDED':True,'quads':len(q),'triangles':len(faces),
        'default_cross_axis':0 if len(q)==3 else 1,
        'positive_target_sign_count':int(np.count_nonzero(orient>0)),
        'orientation_source':'fixed_negative_axis' if signs is None else 'TARGET_event_sign_at_construction',
        'diagonal_scores_evaluated_before_orientation':True,'post_hoc_face_flips':False,
        'diagonal_math':'copied pinned Stage8D HIP FP32 FMA/reduction with confirmed Stage8E second-triangle correction',
        'mesh_cleanup':False}
    return faces,oriented_quads,arrays,detail
