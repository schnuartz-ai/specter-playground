// includes libsecp with preallocated rangeproof functions
#include "libsecp256k1-config.h"
#include "secp256k1.c"
#include "precomputed_ecmult.c"
#include "precomputed_ecmult_gen.c"

#ifdef ENABLE_MODULE_RANGEPROOF
#ifdef ENABLE_MODULE_RANGEPROOF_PREALLOCATED
#include "rangeproof_preallocated/rangeproof_preallocated_impl.h"
#endif
#endif