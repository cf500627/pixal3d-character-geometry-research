"""Identity-free numeric validation for the Stage8G.5 research candidate.

This file never imports supervision or opens data. Validation of a candidate
is not a claim that its ambiguity inventory has a unique geometric solution.
"""
import numpy as np

V2_FIELDS = {
    'event_t_class', 'event_status', 'patch_orbit', 'patch_status',
    'face_arc_status', 'face_arc_offset_fp64', 'face_arc_geometric_moments',
    'ambiguity_cell_xyz', 'ambiguity_kind', 'ambiguity_position',
    'ambiguity_patch_offsets', 'ambiguity_patch_slot', 'ambiguity_status',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def array(data, name, dtype, shape):
    a = data[name]
    require(a.dtype == np.dtype(dtype) and a.shape == shape,
            'Explicit V2 dtype/shape: ' + name)
    require(np.isfinite(a).all(), 'Finite V2 field: ' + name)
    return a


def validate(data):
    """Check stored multiplicity and CSR; retain every member and every token."""
    n = len(data['event_t']); p = len(data['patch_cell_xyz'])
    r = len(data['face_arc_axis']); g = int(data['grid_size'])
    tclass = array(data, 'event_t_class', 'uint32', (n,))
    es = array(data, 'event_status', 'uint8', (n,))
    orbit = array(data, 'patch_orbit', 'uint32', (p,))
    ps = array(data, 'patch_status', 'uint8', (p,))
    ars = array(data, 'face_arc_status', 'uint8', (r,))
    centroid = array(data, 'face_arc_offset_fp64', 'float64', (r, 2))
    moments = array(data, 'face_arc_geometric_moments', 'float64', (r, 4))
    require(np.all(es <= 2) and np.all(ps <= 2) and np.all(ars <= 2), 'Known status enums')
    require(np.all((centroid >= 0) & (centroid <= 1)), 'Face-local centroids')
    require(np.array_equal(centroid.astype(np.float32), data['face_arc_offset']),
            'FP64 centroid must round to the stored reconstruction centroid')
    require(np.all(moments[:, 0] >= 0) and np.all(moments[:, 1] >= 0)
            and np.all(moments[:, 3] >= 0), 'Nonnegative arc length/variance')
    eo = data['event_owner_xyz']; ea = data['event_axis']; et = data['event_t']
    first = np.r_[True, np.any(eo[1:] != eo[:-1], axis=1) | (ea[1:] != ea[:-1])]
    same = np.flatnonzero(~first)
    require(np.all(tclass[first] == 0), 'Distinct-t class starts at zero per edge')
    require(np.all(et[same] >= et[same - 1]), 'Exact event t is nondecreasing')
    require(np.all(tclass[same] == tclass[same - 1] + (et[same] != et[same - 1])),
            'Distinct-t classes exactly retain equal t multiplicity')
    tied = np.zeros(n, bool)
    equal = same[et[same] == et[same - 1]]
    tied[equal] = True; tied[equal - 1] = True
    require(np.all(es[tied] >= 1) and np.all(es[~tied] == 0),
            'Every same-t member is explicit; unique events have regular status')
    pc = data['patch_cell_xyz']
    pfirst = np.r_[True, np.any(pc[1:] != pc[:-1], axis=1)]
    require(np.all(orbit[pfirst] == 0), 'Patch orbits restart at each physical cell')
    ii = np.flatnonzero(~pfirst)
    require(np.all((orbit[ii] == orbit[ii - 1]) | (orbit[ii] == orbit[ii - 1] + 1)),
            'Local orbit labels are contiguous, never global sheet labels')
    require(np.all(ars[data['face_arc_endpoint_count'] == 1] >= 1),
            'One-ended arcs preserve explicit original boundary status')
    a = len(data['ambiguity_kind'])
    cell = array(data, 'ambiguity_cell_xyz', 'int32', (a, 3))
    kind = array(data, 'ambiguity_kind', 'uint8', (a,))
    pos = array(data, 'ambiguity_position', 'float64', (a, 3))
    off = array(data, 'ambiguity_patch_offsets', 'uint64', (a + 1,))
    slots = array(data, 'ambiguity_patch_slot', 'uint32', (len(data['ambiguity_patch_slot']),))
    status = array(data, 'ambiguity_status', 'uint8', (a,))
    require(np.all((cell >= 0) & (cell < g)) and np.all((pos >= 0) & (pos <= 1)),
            'Ambiguity token uses a cell-local numeric position')
    require(np.isin(kind, [1, 2, 3, 4, 5]).all() and np.all(status <= 1), 'Known ambiguity enums')
    require(off[0] == 0 and off[-1] == len(slots) and np.all(off[1:] >= off[:-1]),
            'Complete variable-length ambiguity CSR, without truncation')
    # Resolve every optional contact-to-patch link only by cell xyz + local slot.
    def cellcode(x):
        x = x.astype(np.int64)
        return (x[:, 0] * g + x[:, 1]) * g + x[:, 2]
    radix = int(data['patch_slot'].max(initial=0)) + 1
    patchkey = cellcode(pc) * radix + data['patch_slot']
    owner = np.repeat(np.arange(a), np.diff(off).astype(np.int64))
    contactkey = cellcode(cell[owner]) * radix + slots
    hit = np.searchsorted(patchkey, contactkey)
    require(np.all(slots < radix) and np.all(hit < p)
            and np.array_equal(patchkey[np.minimum(hit, p - 1)], contactkey),
            'Every ambiguity membership resolves to a stored local numeric patch')
    return {
        'multiplicity_member_count': int(tied.sum()),
        'multiplicity_group_count': int(np.sum(tied & np.r_[True, first[1:] | (et[1:] != et[:-1])])),
        'explicit_ambiguity_token_count': a,
        'unresolved_ambiguity_token_count': int(np.sum(status == 1)),
        'ambiguous_arc_count': int(np.sum(ars == 2)),
        'branch_patch_count': int(np.sum(ps == 1)),
        'permutation_orbit_patch_count': int(np.sum(ps == 2)),
        'ambiguity_tokens_used_as_skip_masks': False,
        'SOURCE_identity_fields_used': False,
        'canonical_tie_rule_requires_separate_reindex_equivalence_evidence': True,
        'full_local_topology_closed': bool(a == 0 and np.all(ars != 2)),
        'scope': 'All regular event polygons are constructed. Inventory tokens do not themselves triangulate a branch or an interior-only surface.',
    }


def patch_order(le, event, p, cell, offset, orbit, t, sign):
    """Full event-incidence signature first; no arbitrary SOURCE tie keys."""
    starts = np.flatnonzero(np.r_[True, p[1:] != p[:-1]])
    ends = np.r_[starts[1:], len(p)]
    same = np.flatnonzero(np.any(cell[1:] != cell[:-1], axis=1) == 0) + 1
    def key(i):
        sl = slice(starts[i], ends[i])
        return (tuple(zip(le[sl].tolist(), t[event[sl]].tolist(), sign[event[sl]].tolist())),
                tuple(offset[i].tolist()))
    for i in same:
        left, right = key(i - 1), key(i)
        require(left <= right, 'Patch slots follow complete numerical incidence signature and offset')
        if left < right:
            require(orbit[i] == orbit[i - 1] + 1, 'Distinct numerical patch descriptors have distinct local orbits')
        # Equal primary keys are checked after complete target arc association.


def arc_order(lower, axis, count, le, rank, offset, moments):
    """Use both endpoint signatures when a shared minimum alone cannot order."""
    same = np.flatnonzero((np.all(lower[1:] == lower[:-1], axis=1)) & (axis[1:] == axis[:-1])) + 1
    def key(i):
        return (tuple(zip(le[i, :count[i]].tolist(), rank[i, :count[i]].tolist())),
                tuple(offset[i].tolist()), tuple(moments[i].tolist()))
    for i in same:
        require(key(i - 1) <= key(i), 'Arc slots follow complete endpoint signature and centroid')


def complete_patch_order(data, trace):
    """Finish tied patch ordering using only the saved target face-arc graph."""
    cell=data['patch_cell_xyz']; p=data['incidence_patch']; le=data['incidence_local_edge']
    ranks=data['incidence_event_rank']; eo=data['event_owner_xyz']; ea=data['event_axis']
    er=data['event_rank']; et=data['event_t']; sign=data['event_sign']; g=int(data['grid_size'])
    starts=np.flatnonzero(np.r_[True,p[1:]!=p[:-1]]);ends=np.r_[starts[1:],len(p)]
    rb=int(er.max())+1
    begin=np.array(((0,1,1),(1,0,1),(1,1,0)),np.int64)
    def code(x,a):
        x=x.astype(np.int64)+1
        return (((x[:,0]*(g+2)+x[:,1])*(g+2)+x[:,2])*3+a)
    ek=code(eo,ea)*rb+er
    ia=(le//4).astype(np.int64);physical=cell[p].astype(np.int64).copy();rr=np.arange(len(p))
    physical[rr,(ia+1)%3]+=(le%4)//2;physical[rr,(ia+2)%3]+=le%2
    ie=np.searchsorted(ek,code(physical-begin[ia],ia)*rb+ranks)
    def primary(i):
        sl=slice(starts[i],ends[i]);ev=ie[sl]
        return (tuple(zip(le[sl].tolist(),et[ev].tolist(),sign[ev].tolist())),tuple(data['patch_offset_u8'][i].tolist()))
    same=np.flatnonzero(np.all(cell[1:]==cell[:-1],axis=1))+1
    ties=[]
    for i in same:
        if primary(i-1)==primary(i):ties.append(int(i))
    wanted=set(ties)|{i-1 for i in ties}
    descriptors={i:[] for i in wanted}
    pairs=trace['arc_patch_pairs']
    selected=np.flatnonzero(np.isin(pairs[:,0],list(wanted))|np.isin(pairs[:,1],list(wanted))) if wanted else []
    for j in selected:
        lower=data['face_arc_lower_cell_xyz'][j];axis=int(data['face_arc_axis'][j]); ep=[]
        for k in range(int(data['face_arc_endpoint_count'][j])):
            edge=int(data['face_arc_endpoint_local_edge'][j,k]);ra=int(data['face_arc_endpoint_rank'][j,k]);ax=edge//4
            xyz=lower.astype(np.int64).copy();xyz[(ax+1)%3]+=(edge%4)//2;xyz[(ax+2)%3]+=edge%2
            key=int(code((xyz-begin[ax])[None],np.array([ax]))[0])*rb+ra
            ev=int(np.searchsorted(ek,key));require(ev<len(ek) and ek[ev]==key,'Saved arc event must exist')
            ep.append((edge,float(et[ev]),int(sign[ev])))
        value=(tuple(lower.tolist()),axis,tuple(sorted(ep)),tuple(data['face_arc_offset_fp64'][j].tolist()),tuple(data['face_arc_geometric_moments'][j].tolist()))
        for patch in pairs[j]:
            if int(patch) in descriptors:descriptors[int(patch)].append(value)
    for i in descriptors:descriptors[i]=tuple(sorted(descriptors[i]))
    orbit=data['patch_orbit'];identical=0
    for i in ties:
        left,right=descriptors[i-1],descriptors[i]
        require(left<=right,'Full target numeric patch/arc descriptor ordering')
        require(int(orbit[i])==int(orbit[i-1])+(left!=right),'Explicit orbit agrees with complete stored numerical descriptor')
        identical+=int(left==right)
    return {'equal_primary_patch_pairs_checked':len(ties),'complete_numeric_permutation_pairs':identical,
            'stored_arc_descriptor_order_checked':True,'SOURCE_data_used':False}
