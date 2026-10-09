"""SOURCE-free selective initial triangulation of a local target cell complex.

Face arcs carry distinct local topological edges. The triangulation is chosen
before publishing any mesh: parallel arc identities get shared arc vertices;
ambiguous repeated quad diagonals get a unique event point. No face is deleted,
no mesh is cleaned, and no winding is propagated or repaired.
"""
import numpy as np

ARC_FIELDS={'face_arc_lower_cell_xyz','face_arc_axis','face_arc_slot',
    'face_arc_endpoint_count','face_arc_endpoint_local_edge','face_arc_endpoint_rank','face_arc_offset'}
STARTS=np.array(((0,1,1),(1,0,1),(1,1,0)),np.int64)
SUPPORT=np.array((((0,0,0),(0,0,1),(0,1,1),(0,1,0)),
    ((0,0,0),(1,0,0),(1,0,1),(0,0,1)),
    ((0,0,0),(0,1,0),(1,1,0),(1,0,0))),np.int64)

def require(ok,message):
    if not ok:raise ValueError(message)

def construct(data,vertices,blueprint_faces,oriented_quads,trace,detail):
    lower=data['face_arc_lower_cell_xyz'];axis=data['face_arc_axis'];slot=data['face_arc_slot']
    count=data['face_arc_endpoint_count'];le=data['face_arc_endpoint_local_edge'];rank=data['face_arc_endpoint_rank'];offset=data['face_arc_offset']
    o=data['event_owner_xyz'];ea=data['event_axis'];er=data['event_rank'];sign=data['event_sign']
    pcell=data['patch_cell_xyz'];q=trace['base_quads'];n=len(q);p=len(vertices);k=len(lower);g=int(data['grid_size'])
    for field in ARC_FIELDS:
        a=data[field];require(a.dtype.kind in 'iu f'.replace(' ','') and not a.dtype.hasobject and np.isfinite(a).all(),'Finite numeric local face arcs: '+field)
    require(lower.dtype==np.int32 and lower.shape==(k,3) and k>0,'Face lower cell int32[K,3]')
    require(axis.dtype==np.uint8 and axis.shape==(k,) and np.all(axis<3),'Face axis schema')
    require(slot.dtype==np.uint32 and slot.shape==(k,),'Canonical local face slot schema')
    require(count.dtype==np.uint8 and count.shape==(k,) and np.isin(count,[1,2]).all(),'One or two endpoints per current regular face arc')
    require(le.dtype==np.uint8 and rank.dtype==np.uint32 and le.shape==rank.shape==(k,2),'Face endpoint schema')
    require(offset.dtype==np.float32 and offset.shape==(k,2) and ((offset>=0)&(offset<=1)).all(),'Numeric local face centroid UV')
    require(((lower>=0)&(lower<g)).all() and np.all(lower[np.arange(k),axis]<g-1),'Interior shared faces only')
    require(np.all(le<12) and np.all(le[count==1,1]==0) and np.all(rank[count==1,1]==0),'Masked absent endpoint must have exact zero placeholder')
    canonical=np.lexsort((slot,axis,lower[:,2],lower[:,1],lower[:,0]))
    require(np.array_equal(canonical,np.arange(k)),'Canonical physical face then local slot order')
    starts=np.r_[True,np.any(lower[1:]!=lower[:-1],axis=1)|(axis[1:]!=axis[:-1])]
    same=np.flatnonzero(~starts)
    require(np.all(slot[starts]==0) and np.all(slot[same]==slot[same-1]+1),'Contiguous local face arc slots')
    rank_base=int(er.max())+1
    esig=le.astype(np.int64)*rank_base+rank
    require(np.all(esig[count==2,0]<esig[count==2,1]),'Endpoint geometric signatures sorted')
    import target_v2_validation02 as validation
    validation.arc_order(lower,axis,count,le,rank,data['face_arc_offset_fp64'],data['face_arc_geometric_moments'])
    def edgecode(owner,a):
        xyz=owner.astype(np.int64)+1
        return (((xyz[:,0]*(g+2)+xyz[:,1])*(g+2)+xyz[:,2])*3+a)
    event_key=edgecode(o,ea)*rank_base+er
    keep=np.arange(2)[None,:]<count[:,None]
    arc_id=np.repeat(np.arange(k,dtype=np.int64),count)
    local_edge=le[keep].astype(np.int64);endpoint_rank=rank[keep]
    la=local_edge//4;first=(local_edge%4)//2;second=local_edge%2
    physical=lower[arc_id].astype(np.int64).copy();rr=np.arange(len(arc_id))
    physical[rr,(la+1)%3]+=first;physical[rr,(la+2)%3]+=second
    require(np.all(la!=axis[arc_id]) and np.all(physical[rr,axis[arc_id]]==lower[arc_id,axis[arc_id]]+1),'Endpoint edge lies on this physical face')
    eo=physical-STARTS[la]
    require(np.all(endpoint_rank<rank_base),'Endpoint event rank exists')
    key=edgecode(eo,la)*rank_base+endpoint_rank
    event=np.searchsorted(event_key,key)
    require(np.all(event<n) and np.array_equal(event_key[np.minimum(event,n-1)],key),'Every face endpoint resolves from target geometry')
    delta=lower[arc_id].astype(np.int64)-o[event]
    upper_delta=delta.copy();upper_delta[rr,axis[arc_id]]+=1
    sl=np.all(delta[:,None,:]==SUPPORT[la],axis=2);su=np.all(upper_delta[:,None,:]==SUPPORT[la],axis=2)
    require(np.all(sl.sum(axis=1)==1) and np.all(su.sum(axis=1)==1),'Both cells physically support endpoint event')
    jl=sl.argmax(axis=1);ju=su.argmax(axis=1)
    adjacent=((jl+1)%4==ju)|((ju+1)%4==jl)
    require(adjacent.all(),'Shared face must connect adjacent event support cells')
    side=np.where((jl+1)%4==ju,jl,ju)
    event_side=event*4+side
    require(np.array_equal(np.sort(event_side),np.arange(n*4)),'Each target event has exactly four distinct face-arc memberships')
    pair=np.stack((q[event,jl],q[event,ju]),axis=1)
    require(np.all(pair[:,0]!=pair[:,1]),'Arc connects two distinct cell patches')
    begin=np.r_[0,np.cumsum(count,dtype=np.int64)[:-1]]
    two=np.flatnonzero(count==2)
    require(np.array_equal(pair[begin[two]],pair[begin[two]+1]),'Both arc endpoints agree on both local patch assignments')
    arc_pair=pair[begin]
    emap=np.empty((n,4),np.int32);emap.reshape(-1)[event_side]=arc_id
    # Multiple explicit arcs with the same patch pair cannot share an indexed edge.
    pc=arc_pair.min(axis=1).astype(np.int64)*p+arc_pair.max(axis=1)
    _,pinverse,pcounts=np.unique(pc,return_inverse=True,return_counts=True)
    split_arc=pcounts[pinverse]>1
    # An internal diagonal is private to one event polygon. Repeated support
    # pairs would incorrectly identify different topological diagonals.
    d0=np.where(trace['chosen_pattern']==0,q[:,0],q[:,1])
    d1=np.where(trace['chosen_pattern']==0,q[:,2],q[:,3])
    dc=np.minimum(d0,d1).astype(np.int64)*p+np.maximum(d0,d1)
    _,dinverse,dcounts=np.unique(dc,return_inverse=True,return_counts=True)
    split_event_diagonal=dcounts[dinverse]>1
    edge_insert=split_arc[emap]
    refined=np.any(edge_insert,axis=1)|split_event_diagonal
    selected_arcs=np.flatnonzero(split_arc);selected_events=np.flatnonzero(refined)
    av=np.full(k,-1,np.int32);av[selected_arcs]=np.arange(p,p+len(selected_arcs),dtype=np.int32)
    arc_grid=lower[selected_arcs].astype(np.float32)
    aa=axis[selected_arcs].astype(np.int64);ar=np.arange(len(aa))
    arc_grid[ar,aa]+=np.float32(1)
    arc_grid[ar,(aa+1)%3]+=offset[selected_arcs,0]
    arc_grid[ar,(aa+2)%3]+=offset[selected_arcs,1]
    arc_vertices=arc_grid/np.float32(g)-np.float32(.5)
    # Event vertices are uniquely indexed and their numeric t is sufficient.
    event_grid=o[selected_events].astype(np.float64)+STARTS[ea[selected_events]]
    event_grid[np.arange(len(selected_events)),ea[selected_events]]+=data['event_t'][selected_events]
    event_vertices=(event_grid/g-.5).astype(np.float32)
    # C2: select an initial fan center from a fixed, nonzero blend of the
    # numeric edge-event point and the boundary polygon mean. Only low-quality
    # baseline fans trigger selection. No emitted triangle or SOURCE is input.
    # Every candidate stays in the convex hull of these numeric target points;
    # nonzero event contribution preserves separation of distinct crossings.
    support_vertices=np.concatenate((vertices,arc_vertices),axis=0)
    blend_lambdas=np.ones(len(selected_events),np.float32)
    center_changed=0
    def quality(center,poly):
        c64=center.astype(np.float64);v64=poly.astype(np.float64)
        nxt=np.roll(v64,-1,axis=0)
        area=np.linalg.norm(np.cross(v64-c64,nxt-c64),axis=1)
        longest=np.maximum.reduce((np.sum((v64-c64)**2,axis=1),np.sum((nxt-c64)**2,axis=1),np.sum((nxt-v64)**2,axis=1)))
        aspect=np.divide(longest,area,out=np.full(len(area),np.inf),where=area>0)
        return (int((area==0).sum()),int((aspect>100).sum()),float(aspect.max()),float(np.minimum(aspect,1e12).sum()))
    for j,e in enumerate(selected_events):
        ids=[]
        for side_index in range(4):
            ids.append(int(q[e,side_index]))
            if av[emap[e,side_index]]>=0:ids.append(int(av[emap[e,side_index]]))
        poly=support_vertices[np.array(ids,np.int32)]
        original_center=event_vertices[j].copy()
        best=quality(original_center,poly)
        if best[0]==0 and best[1]==0:continue
        mean=poly.astype(np.float64).mean(axis=0)
        for coefficient in (.75,.5,.25,.125):
            candidate=(coefficient*original_center.astype(np.float64)+(1-coefficient)*mean).astype(np.float32)
            score=quality(candidate,poly)
            if score<best:
                event_vertices[j]=candidate;best=score;blend_lambdas[j]=coefficient
        center_changed+=int(blend_lambdas[j]!=1)
    final_vertices=np.concatenate((vertices,arc_vertices,event_vertices),axis=0)
    require(np.isfinite(final_vertices).all(),'Finite geometry at initial construction')
    dense=np.full((n,8),-1,np.int32);dense[:,::2]=q;dense[:,1::2]=av[emap]
    positive=sign>0
    dense[positive]=dense[positive][:,[0,7,6,5,4,3,2,1]]
    degree=(dense>=0).sum(axis=1).astype(np.int64)
    poff=np.r_[0,np.cumsum(degree,dtype=np.int64)]
    polygons=dense[dense>=0]
    triangle_count=np.where(refined,degree,2)
    triangle_offsets=np.r_[0,np.cumsum(triangle_count,dtype=np.int64)]
    faces=np.empty((triangle_offsets[-1],3),np.int32)
    ordinary=np.flatnonzero(~refined)
    old=blueprint_faces.reshape(n,2,3)
    faces[triangle_offsets[ordinary]]=old[ordinary,0]
    faces[triangle_offsets[ordinary]+1]=old[ordinary,1]
    event_vertex_start=p+len(selected_arcs)
    for j,e in enumerate(selected_events):
        poly=polygons[poff[e]:poff[e+1]]
        tri=np.stack((np.full(len(poly),event_vertex_start+j,np.int32),poly,np.roll(poly,-1)),axis=1)
        faces[triangle_offsets[e]:triangle_offsets[e+1]]=tri
    require(np.all(faces>=0) and np.all(faces<len(final_vertices)),'Legal final triangles')
    require(np.all(faces[:,0]!=faces[:,1]) and np.all(faces[:,1]!=faces[:,2]) and np.all(faces[:,0]!=faces[:,2]),'No repeated-index triangle')
    trace.update(polygon_offsets=poff,polygon_vertices=polygons,
        selected_arc_target_rows=selected_arcs.astype(np.int32),selected_event_center_rows=selected_events.astype(np.int32),
        event_triangle_offsets=triangle_offsets,arc_patch_pairs=arc_pair,fan_center_event_blend_lambda=blend_lambdas,
        event_side_arc=emap,parallel_arc_mask=split_arc,repeated_diagonal_mask=split_event_diagonal)
    detail.update(representation='V1-C2 local numeric face arcs + bounded initial fan-center construction',fan_centers_changed=center_changed,fan_center_rule='If baseline fan contains zero area or aspect>100, lexicographic zero/aspect-count/max-aspect/sum-aspect selection among event/mean blends lambda1,.75,.5,.25,.125; no zero lambda',
        face_arc_count=k,selected_arc_vertices=len(selected_arcs),selected_event_vertices=len(selected_events),
        repeated_diagonal_event_count=int(split_event_diagonal.sum()),unchanged_original_two_triangle_events=int((~refined).sum()),
        output_vertices=len(final_vertices),output_faces=len(faces),
        polygon_degree_histogram={str(i):int((degree==i).sum()) for i in range(4,9)},
        base_quads_are_control_only=True,source_identity_or_adjacency_used=False,
        SOURCE_ACCESSED='NO',mesh_cleanup=False,post_hoc_face_deletion=False,
        final_winding='event sign applied during polygon construction; no BFS or normal propagation',
        arc_position='numeric target face-local polyline centroid',event_position='numeric edge t point, with recorded bounded polygon-mean blend where initial fan quality requires it')
    return final_vertices,faces,oriented_quads,trace,detail
