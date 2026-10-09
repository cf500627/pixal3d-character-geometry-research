// Only the two upstream hash operations actually called by eval mesh extraction.
#include "src/api.h"
PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) {
    m.def("hashmap_insert_3d_idx_as_val_cuda", &hashmap_insert_3d_idx_as_val_cuda);
    m.def("hashmap_lookup_3d_cuda", &hashmap_lookup_3d_cuda);
}
