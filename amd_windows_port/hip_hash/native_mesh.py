"""Process-only binding of unchanged upstream eval geometry to two native HIP ops."""
from pathlib import Path
import importlib.util,sys,torch
_CALLS=[]
def install(extension_directory, grid_size=1024):
    sys.path.insert(0,str(extension_directory))
    import _stage7e_hash
    import o_voxel
    import o_voxel.convert as convert
    # Additional symbols only in this process; the preserved CPU module on disk is unchanged.
    for name in ('hashmap_insert_3d_idx_as_val_cuda','hashmap_lookup_3d_cuda'):
        native=getattr(_stage7e_hash,name)
        def wrapped(*args,_native=native,_name=name):
            assert not torch.is_grad_enabled() and all(x.device.type=='cuda' for x in args if isinstance(x,torch.Tensor))
            assert torch.cuda.current_stream()==torch.cuda.default_stream(), 'Upstream kernels launch on default stream'
            _CALLS.append(_name)
            return _native(*args)
        setattr(o_voxel._C,name,wrapped)
    source=Path(__file__).resolve().parent/'vendor/flexible_dual_grid.py'
    spec=importlib.util.spec_from_file_location('o_voxel.convert._stage7e_upstream',source)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    upstream=module.flexible_dual_grid_to_mesh
    def extraction(coords,vertices,flags,q=None,**kwargs):
        assert kwargs.get('train',False) is False
        assert coords.dtype==torch.int32 and coords.ndim==2 and coords.shape[1]==3
        assert coords.is_cuda and vertices.is_cuda and flags.is_cuda
        assert len(coords)>0 and len(coords)==len(vertices)==len(flags)
        assert torch.isfinite(vertices).all().item()
        if q is not None: assert q.is_cuda and torch.isfinite(q).all().item() and (q>0).all().item()
        grid=kwargs.get('grid_size',None);assert grid==grid_size
        assert ((coords>=0)&(coords<grid)).all().item()
        code=coords[:,0].to(torch.int64)*grid*grid+coords[:,1].to(torch.int64)*grid+coords[:,2].to(torch.int64)
        assert code.unique().numel()==len(code),'Duplicate coordinates rejected'
        return upstream(coords.contiguous(),vertices.contiguous(),flags.contiguous(),None if q is None else q.contiguous(),**kwargs)
    convert.flexible_dual_grid_to_mesh=extraction
    return extraction
def calls(): return list(_CALLS)
def cleanup():
    module=sys.modules.get('o_voxel.convert._stage7e_upstream')
    if module is not None:
        func=module.flexible_dual_grid_to_mesh
        for name in ('edge_neighbor_voxel_offset','quad_split_1','quad_split_2','quad_split_train'):
            if hasattr(func,name):delattr(func,name)
