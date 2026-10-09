"""Research V2 numeric assembler, copied without algorithm changes.

The historical Windows audit/launcher CLI is omitted. This library does not
install its own file-access sandbox. Call reconstruct(data) with numeric arrays
matching the strict whitelist; no SOURCE or training data is loaded here.
"""

BASE_FIELDS = {'grid_size','event_owner_xyz','event_axis','event_rank','event_t',
    'event_sign','patch_cell_xyz','patch_slot','patch_offset','patch_offset_u8',
    'incidence_patch','incidence_local_edge','incidence_event_rank'}


NORMAL_FIELDS = {'event_normal','patch_normal'}


V2_FIELDS = {'event_t_class','event_status','patch_orbit','patch_status','face_arc_status','face_arc_offset_fp64','face_arc_geometric_moments','ambiguity_cell_xyz','ambiguity_kind','ambiguity_position','ambiguity_patch_offsets','ambiguity_patch_slot','ambiguity_status'}


ARC_FIELDS={'face_arc_lower_cell_xyz','face_arc_axis','face_arc_slot','face_arc_endpoint_count','face_arc_endpoint_local_edge','face_arc_endpoint_rank','face_arc_offset'}


STARTS = ((0,1,1),(1,0,1),(1,1,0))


SUPPORT = (((0,0,0),(0,0,1),(0,1,1),(0,1,0)),
           ((0,0,0),(1,0,0),(1,0,1),(0,0,1)),
           ((0,0,0),(0,1,0),(1,1,0),(1,0,0)))


def require(condition, message):
    if not condition: raise ValueError(message)


def quad_blueprint(data, v2):
    import numpy as np
    import target_triangle_emission as emission
    keys=set(data)
    require(keys in (BASE_FIELDS, BASE_FIELDS|NORMAL_FIELDS), 'Target fields must match explicit numeric schema; identity or unknown fields rejected')
    for k,v in data.items():
        require(v.dtype.kind in 'biuf' and not v.dtype.hasobject, 'Numeric non-object arrays only: '+k)
        require(np.isfinite(v).all(), 'Nonfinite target value: '+k)
    grid=data['grid_size']
    require(grid.size==1 and grid.dtype.kind in 'iu' and int(grid)==1024,'Frozen resolution 1024 target only; no model execution')
    g=int(grid)
    o=data['event_owner_xyz']; axis=data['event_axis']; rank=data['event_rank']; t=data['event_t']; sign=data['event_sign']
    cell=data['patch_cell_xyz']; slot=data['patch_slot']; offset=data['patch_offset']; u8=data['patch_offset_u8']
    p=data['incidence_patch']; le=data['incidence_local_edge']; ir=data['incidence_event_rank']
    n=len(o); patches=len(cell)
    require(o.shape==(n,3) and o.dtype==np.int32 and n>0,'event_owner_xyz must be nonempty int32[N,3]')
    require(axis.shape==rank.shape==t.shape==sign.shape==(n,), 'Event field lengths')
    require(axis.dtype==np.uint8 and rank.dtype==np.uint32 and t.dtype==np.float64 and sign.dtype==np.int8,'Event field dtypes')
    require(np.all(axis<3) and np.isin(sign,[-1,1]).all() and ((t>0)&(t<1)).all(),'Regular proper events only; explicit special-event schema needed for degeneracy')
    require(np.all((o>=-1)&(o<g)), 'Event coordinate domain')
    require(cell.shape==(patches,3) and cell.dtype==np.int32 and slot.dtype==np.uint32 and slot.shape==(patches,), 'Patch coordinate/slot schema')
    require(np.all((cell>=0)&(cell<g)), 'Patch cells in domain')
    require(offset.dtype==np.float32 and offset.shape==(patches,3) and u8.dtype==np.uint8 and u8.shape==offset.shape, 'Patch QEF schema')
    require(np.array_equal(offset,u8.astype(np.float32)/np.float32(255)), 'Dequantization must exactly preserve frozen QEF math')
    require(p.dtype==np.uint32 and le.dtype==np.uint8 and ir.dtype==np.uint32 and p.shape==le.shape==ir.shape, 'Incidence schema')
    require(len(p)==4*n and np.all(p<patches) and np.all(le<12), 'Every current interior event needs exactly four supports, without truncation')
    order=np.lexsort((rank,axis,o[:,2],o[:,1],o[:,0]))
    require(np.array_equal(order,np.arange(n)), 'Canonical event geometry order required')
    order=np.lexsort((slot,cell[:,2],cell[:,1],cell[:,0]))
    require(np.array_equal(order,np.arange(patches)), 'Canonical local patch order required')
    order=np.lexsort((ir,le,p))
    require(np.array_equal(order,np.arange(len(p))), 'Canonical incidence order required')
    fresh=np.r_[True,np.any(cell[1:]!=cell[:-1],axis=1)]
    require(np.all(slot[fresh]==0) and np.all(slot[~fresh]==(slot[np.flatnonzero(~fresh)-1]+1)), 'Contiguous local patch slots, never global sheet IDs')
    def edgecode(owner,axes):
        xyz=owner.astype(np.int64)+1
        return (((xyz[:,0]*(g+2)+xyz[:,1])*(g+2)+xyz[:,2])*3+axes)
    ec=edgecode(o,axis)
    edge_start=np.r_[True,ec[1:]!=ec[:-1]]
    require(np.all(rank[edge_start]==0), 'Event ranks start at zero per edge')
    ii=np.flatnonzero(~edge_start)
    require(np.all(rank[ii]==rank[ii-1]+1) and np.all(t[ii]>=t[ii-1]), 'Ranks retain all same-t members; explicit V2 t classes checked separately')
    rank_base=int(rank.max())+1
    require(int(ec.max())*rank_base+int(rank.max())<np.iinfo(np.int64).max, 'Dynamic lookup integer overflow')
    key=ec*rank_base+rank
    require(np.all(key[1:]>key[:-1]), 'Unique canonical event keys')
    ia=(le//4).astype(np.int64); b0=(le%4)//2; b1=le%2
    physical=cell[p].astype(np.int64).copy()
    rows=np.arange(len(p))
    physical[rows,(ia+1)%3]+=b0
    physical[rows,(ia+2)%3]+=b1
    io=physical-np.array(STARTS,np.int64)[ia]
    ikey=edgecode(io,ia)*rank_base+ir
    require(np.all(ir<rank_base), 'Unknown event rank in patch incidence')
    event=np.searchsorted(key,ikey)
    require(np.all(event<n) and np.array_equal(key[np.minimum(event,n-1)],ikey), 'Every incidence must identify one target event geometrically')
    delta=cell[p].astype(np.int64)-o[event]
    matches=np.all(delta[:,None,:]==np.array(SUPPORT,np.int64)[ia],axis=2)
    require(np.all(matches.sum(axis=1)==1),'Incidence must belong to one of the four physical support cells')
    side=matches.argmax(axis=1)
    flat_index=event*4+side
    require(np.array_equal(np.sort(flat_index),np.arange(n*4)), 'Exactly one patch assignment per event support, no missing or duplicate incidence')
    first=np.flatnonzero(np.r_[True,p[1:]!=p[:-1]])
    require(len(first)==patches, 'Every patch has an event incidence')
    signature_first=le[first].astype(np.int64)*rank_base+ir[first]
    same_cell=np.flatnonzero(~fresh)
    import target_v2_validation02 as validation
    validation.patch_order(le,event,p,cell,offset,v2['patch_orbit'],t,sign)
    quads=np.empty((n,4),np.int32)
    quads.reshape(-1)[flat_index]=p
    require(np.array_equal(np.unique(p),np.arange(patches)), 'No inactive/fabricated patch vertices in this edge-event schema')
    vertices=(cell.astype(np.float32)+offset)/np.float32(g)-np.float32(.5)
    normals_present=bool(keys&NORMAL_FIELDS)
    if normals_present:
        require(data['event_normal'].shape==(n,3) and data['patch_normal'].shape==(patches,3), 'Numeric normal descriptor shapes')
        require(data['event_normal'].dtype.kind=='f' and data['patch_normal'].dtype.kind=='f', 'Normal descriptor floating point')
        # Exact incidence and explicit event sign make normals redundant for connectivity/winding here.
    faces,oriented,trace,detail=emission.emit(vertices,quads,sign)
    detail.update(target_normal_fields_present=normals_present, normal_fields_used_for_matching=False,
        normal_fields_used_for_orientation=False, source_geometry_or_identity_used=False,
        event_count=n,patch_count=patches,incidence_count=len(p),grid=g, rank_capacity='VARIABLE_LENGTH_NO_TRUNCATION')
    return vertices,faces,oriented,trace,detail


def reconstruct(data):
    require(set(data) == BASE_FIELDS|ARC_FIELDS|V2_FIELDS, 'Explicit minimum numeric V2 candidate schema only')
    import target_v2_validation02 as validation
    validation_detail=validation.validate(data)
    import target_face_arc_construction_v2_02 as arcs
    base={k:v for k,v in data.items() if k in BASE_FIELDS}
    outputs=arcs.construct(data,*quad_blueprint(base,data))
    validation_detail['complete_patch_canonical_order']=validation.complete_patch_order(data,outputs[3])
    outputs[-1].update(V2_candidate_validation=validation_detail,representation='V2 candidate; unchanged C2 initial geometry construction',all_regular_event_members_constructed=True,ambiguity_inventory_is_not_branch_triangulation=True)
    return outputs


def save_ply(path,vertices,faces):
    import numpy as np
    packed=np.empty(len(faces),dtype=[('n','u1'),('indices','<i4',(3,))])
    packed['n']=3;packed['indices']=faces
    header=('ply\nformat binary_little_endian 1.0\ncomment Stage8G TARGET_ONLY NOT_OFFICIAL\n'
        f'element vertex {len(vertices)}\nproperty float x\nproperty float y\nproperty float z\n'
        f'element face {len(faces)}\nproperty list uchar int vertex_indices\nend_header\n').encode('ascii')
    with path.open('xb') as stream:
        stream.write(header);stream.write(np.asarray(vertices,'<f4').tobytes());stream.write(packed.tobytes())

